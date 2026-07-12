"""
---------------------------------------------------------
CaseStudy AI Backend
MCP Client
---------------------------------------------------------

Purpose:
    Connect to the DeTLeng BigQuery MCP Server.

Responsibilities:
    - Connect to MCP Server
    - Discover MCP Tools
    - Execute MCP Tools
    - Return Results

This module contains NO:
    - OpenAI Logic
    - Business Logic
    - Prompt Logic
"""

import asyncio
import json
import logging
import os
from collections.abc import Mapping, Sequence

from dotenv import load_dotenv
from fastmcp import Client


# =====================================================
# LOAD ENV
# =====================================================

load_dotenv()


# =====================================================
# LOGGING
# =====================================================

logger = logging.getLogger(__name__)


# =====================================================
# MCP SERVER CONFIGURATION
# =====================================================

MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "https://detleng-bigquery-mcp.onrender.com/mcp"
).rstrip("/")

MCP_TIMEOUT_SECONDS = float(os.getenv(
    "MCP_TIMEOUT_SECONDS",
    "30"
))

MCP_MAX_RETRIES = int(os.getenv(
    "MCP_MAX_RETRIES",
    "3"
))

MCP_RETRY_DELAY_SECONDS = float(os.getenv(
    "MCP_RETRY_DELAY_SECONDS",
    "0.75"
))


# =====================================================
# EXCEPTIONS
# =====================================================

class MCPClientError(RuntimeError):
    """
    Base exception for MCP communication failures.
    """


class MCPToolValidationError(MCPClientError):
    """
    Raised when an invalid MCP tool is requested.
    """


class MCPToolExecutionError(MCPClientError):
    """
    Raised when an MCP tool fails after retries.
    """


# =====================================================
# MCP CLIENT
# =====================================================

class MCPClient:

    def __init__(
        self,
        server_url: str = MCP_SERVER_URL,
        timeout_seconds: float = MCP_TIMEOUT_SECONDS,
        max_retries: int = MCP_MAX_RETRIES,
        retry_delay_seconds: float = MCP_RETRY_DELAY_SECONDS,
    ):

        self.server_url = server_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max(1, max_retries)
        self.retry_delay_seconds = max(0, retry_delay_seconds)
        self._tool_cache: set[str] | None = None

    async def list_tools(self, refresh: bool = False) -> list[str]:

        if self._tool_cache is not None and not refresh:
            return sorted(self._tool_cache)

        logger.info(
            "Discovering MCP tools from server: url=%s",
            self.server_url,
        )

        raw_tools = await asyncio.wait_for(
            self._list_tools_once(),
            timeout=self.timeout_seconds,
        )

        tool_names = self._extract_tool_names(raw_tools)
        self._tool_cache = set(tool_names)

        logger.info(
            "Discovered MCP tools: count=%s tools=%s",
            len(tool_names),
            tool_names,
        )

        return sorted(self._tool_cache)

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict | None = None
    ):

        await self._validate_tool_name(tool_name)

        if arguments is None:
            arguments = {}

        if not isinstance(arguments, dict):
            raise MCPToolValidationError(
                "MCP tool arguments must be a dictionary."
            )

        last_error = None

        logger.info(
            "MCP call requested: url=%s tool=%s arguments=%r timeout_seconds=%s max_retries=%s",
            self.server_url,
            tool_name,
            arguments,
            self.timeout_seconds,
            self.max_retries,
        )

        for attempt in range(1, self.max_retries + 1):

            try:

                logger.info(
                    "MCP connection attempt starting: url=%s tool=%s attempt=%s/%s",
                    self.server_url,
                    tool_name,
                    attempt,
                    self.max_retries,
                )

                raw_result = await asyncio.wait_for(
                    self._call_tool_once(tool_name, arguments),
                    timeout=self.timeout_seconds,
                )

                logger.info(
                    "Raw MCP response received: tool=%s attempt=%s/%s response_type=%s response=%r",
                    tool_name,
                    attempt,
                    self.max_retries,
                    type(raw_result).__name__,
                    raw_result,
                )

                extracted_result = self._extract_result(raw_result)

                logger.info(
                    "Extracted MCP response: tool=%s attempt=%s/%s response=%r",
                    tool_name,
                    attempt,
                    self.max_retries,
                    extracted_result,
                )

                return extracted_result

            except asyncio.TimeoutError as exc:

                last_error = exc

                logger.exception(
                    "MCP tool timed out with full traceback: url=%s tool=%s timeout_seconds=%s attempt=%s/%s",
                    self.server_url,
                    tool_name,
                    self.timeout_seconds,
                    attempt,
                    self.max_retries,
                )

            except Exception as exc:

                last_error = exc

                logger.exception(
                    "MCP tool execution failed with full traceback: url=%s tool=%s arguments=%r attempt=%s/%s error_type=%s error=%s",
                    self.server_url,
                    tool_name,
                    arguments,
                    attempt,
                    self.max_retries,
                    type(exc).__name__,
                    exc,
                )

            if attempt < self.max_retries:
                retry_delay = self.retry_delay_seconds * attempt

                logger.info(
                    "Retrying MCP tool after delay: tool=%s delay_seconds=%s next_attempt=%s/%s",
                    tool_name,
                    retry_delay,
                    attempt + 1,
                    self.max_retries,
                )

                await asyncio.sleep(retry_delay)

        logger.error(
            "MCP tool failed after all retries: url=%s tool=%s attempts=%s last_error_type=%s last_error=%s",
            self.server_url,
            tool_name,
            self.max_retries,
            type(last_error).__name__ if last_error else None,
            last_error,
        )

        raise MCPToolExecutionError(
            f"MCP tool '{tool_name}' failed after {self.max_retries} attempts. "
            f"Last error: {type(last_error).__name__}: {last_error}"
        ) from last_error

    async def _list_tools_once(self):

        client = Client(self.server_url)

        async with client:

            logger.info(
                "MCP client connected. Listing tools: url=%s",
                self.server_url,
            )

            return await client.list_tools()

    async def _call_tool_once(
        self,
        tool_name: str,
        arguments: dict
    ):

        client = Client(self.server_url)

        async with client:

            logger.info(
                "MCP client connected. Executing tool: url=%s tool=%s arguments=%r",
                self.server_url,
                tool_name,
                arguments,
            )

            result = await client.call_tool(
                tool_name,
                arguments
            )

            logger.info(
                "MCP tool execution completed: tool=%s",
                tool_name,
            )

            return result

    async def _validate_tool_name(self, tool_name: str):

        if not isinstance(tool_name, str) or not tool_name.strip():
            raise MCPToolValidationError(
                "MCP tool name must be a non-empty string."
            )

        available_tools = await self.list_tools()

        if tool_name not in available_tools:
            raise MCPToolValidationError(
                f"Unsupported MCP tool requested: {tool_name}"
            )

    def _extract_tool_names(self, tools) -> list[str]:

        tool_names = []

        for tool in tools or []:
            if isinstance(tool, str):
                tool_names.append(tool)
                continue

            name = getattr(tool, "name", None)

            if name:
                tool_names.append(name)
                continue

            if isinstance(tool, Mapping) and tool.get("name"):
                tool_names.append(tool["name"])

        return sorted(set(tool_names))

    def _extract_result(self, result):

        if result is None:
            logger.warning("MCP response is None.")
            return None

        if hasattr(result, "is_error") and result.is_error:
            raise MCPToolExecutionError(
                f"MCP server returned an error response: {result}"
            )

        if hasattr(result, "data") and result.data is not None:
            return self._normalize_value(result.data)

        if (
            hasattr(result, "structured_content")
            and result.structured_content is not None
        ):
            return self._normalize_value(result.structured_content)

        if hasattr(result, "content") and result.content:
            extracted_content = [
                self._extract_content_item(item)
                for item in result.content
            ]

            extracted_content = [
                item for item in extracted_content
                if item is not None
            ]

            if len(extracted_content) == 1:
                return extracted_content[0]

            return extracted_content

        if isinstance(result, (dict, list, tuple, str, int, float, bool)):
            return self._normalize_value(result)

        model_dump = getattr(result, "model_dump", None)

        if callable(model_dump):
            return self._normalize_value(model_dump())

        dict_method = getattr(result, "dict", None)

        if callable(dict_method):
            return self._normalize_value(dict_method())

        logger.warning(
            "Returning unnormalized MCP response object: response_type=%s response=%r",
            type(result).__name__,
            result,
        )

        return result

    def _extract_content_item(self, item):

        if item is None:
            return None

        text = getattr(item, "text", None)

        if text is not None:
            return self._parse_text(text)

        data = getattr(item, "data", None)

        if data is not None:
            return self._normalize_value(data)

        resource = getattr(item, "resource", None)

        if resource is not None:
            return self._normalize_value(resource)

        model_dump = getattr(item, "model_dump", None)

        if callable(model_dump):
            return self._normalize_value(model_dump())

        dict_method = getattr(item, "dict", None)

        if callable(dict_method):
            return self._normalize_value(dict_method())

        return item

    def _parse_text(self, text: str):

        stripped_text = text.strip()

        if not stripped_text:
            return ""

        try:
            return self._normalize_value(json.loads(stripped_text))
        except json.JSONDecodeError:
            return stripped_text

    def _normalize_value(self, value):

        if isinstance(value, Mapping):
            return {
                key: self._normalize_value(item)
                for key, item in value.items()
            }

        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return [
                self._normalize_value(item)
                for item in value
            ]

        model_dump = getattr(value, "model_dump", None)

        if callable(model_dump):
            return self._normalize_value(model_dump())

        dict_method = getattr(value, "dict", None)

        if callable(dict_method):
            return self._normalize_value(dict_method())

        return value


# =====================================================
# SINGLETON
# =====================================================

mcp = MCPClient()
