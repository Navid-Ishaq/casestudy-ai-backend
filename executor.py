"""
---------------------------------------------------------
CaseStudy AI Backend
Deterministic MCP Executor
---------------------------------------------------------

Purpose:
    Execute deterministic MCP actions selected by the Python router.

This module contains no OpenAI logic and no prompt logic.
"""

import logging
from typing import Any

from mcp_client import MCPClient
from registry import ToolRoute, group_registered_tools


logger = logging.getLogger(__name__)


KPI_NOT_AVAILABLE_MESSAGE = (
    "This KPI is currently not available through the Business Intelligence layer."
)


async def execute_mcp_tool(
    mcp: MCPClient,
    route: ToolRoute,
) -> Any:

    arguments = route.arguments or {}

    logger.info(
        "Executor calling MCP tool: tool=%s arguments=%r",
        route.tool_name,
        arguments,
    )

    return await mcp.call_tool(
        route.tool_name,
        arguments,
    )


async def get_tool_catalog(mcp: MCPClient) -> dict[str, list[str]]:

    registry_response = await mcp.call_tool(
        "list_registered_tools",
        {},
    )

    if isinstance(registry_response, dict):
        tool_names = registry_response.get("tools", [])
    else:
        tool_names = registry_response

    return group_registered_tools(tool_names)


async def get_dataset_information(mcp: MCPClient) -> dict[str, Any]:

    return await mcp.call_tool(
        "server_status",
        {},
    )


def build_tool_catalog_answer(tool_catalog: dict[str, list[str]]) -> str:

    lines = ["Available Business Intelligence tools:"]

    for category, tools in tool_catalog.items():
        lines.append("")
        lines.append(f"{category}:")

        for tool_name in tools:
            lines.append(f"- {tool_name}")

    return "\n".join(lines)


def build_dataset_answer(dataset_info: dict[str, Any]) -> str:

    project = dataset_info.get("project", "not available")
    dataset = dataset_info.get("dataset", "not available")
    application = dataset_info.get("application", "DeTLeng BigQuery MCP Server")
    status = str(dataset_info.get("server", "not available")).title()

    return (
        "Dataset Information\n\n"
        f"Application: {application}\n"
        f"Status: {status}\n"
        f"Project: {project}\n"
        f"Analytics Dataset: {dataset}"
    )
