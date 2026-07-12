import asyncio
import logging
import os
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field

from executor import (
    KPI_NOT_AVAILABLE_MESSAGE,
    build_dataset_answer,
    build_tool_catalog_answer,
    execute_mcp_tool,
    get_dataset_information,
    get_tool_catalog,
)
from mcp_client import mcp
from registry import Intent, route_question

# ==============================
# LOAD ENV
# ==============================

load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

DEBUG_ROUTER = os.getenv(
    "DEBUG_ROUTER",
    "false"
).lower() == "true"

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4o-mini"
)

LANGUAGE_ENFORCEMENT_MESSAGE = """
You MUST answer in English unless the user explicitly requests another language.

Never infer language from dataset values, product names, customer names, country names, or business data.

If the user explicitly asks for another language, use only that requested language.
"""

# ==============================
# FASTAPI
# ==============================

app = FastAPI(
    title="DeTLeng AI Backend",
    version="1.0"
)

# ==============================
# CORS
# ==============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# KNOWLEDGE
# ==============================

with open(
    "knowledge/detleng_knowledge.txt",
    "r",
    encoding="utf-8"
) as f:

    KNOWLEDGE = f.read()

# ==============================
# REQUEST MODEL
# ==============================

class Question(BaseModel):

    message: str
    history: List[Dict] = Field(default_factory=list)

# ==============================
# HOME
# ==============================

@app.get("/")
def home():

    return {

        "status": "running",
        "service": "DeTLeng AI Backend",
        "version": "1.0"

    }

# ==============================
# CHAT BUILDER
# ==============================

def build_messages(question: Question):

    messages = [

        {
    "role": "system",
    "content": f"""
You are DeTLeng Analytics AI.

Always reply in the SAME language used by the user.

If the user asks in English, answer in English.

If the user asks in Urdu, answer in Urdu.

Never reply in French, Spanish, German or any other language unless the user explicitly asks for it.

You explain analytics returned by the internal Business Intelligence system.

Use the following DeTLeng knowledge when the user asks about DeTLeng services, case studies, or company information:

{KNOWLEDGE}

Rules:

- Never invent numbers.
- Never change numeric values.
- Explain the analytics clearly.
- Give short business insights.
- Give practical recommendations.
- Keep the answer professional.
"""
}

    ]

    for msg in question.history:

        if msg["role"] in ["user", "assistant"]:

            messages.append(msg)

    messages.append({

        "role": "user",
        "content": question.message

    })

    return messages


def enforce_language_policy(messages: List[Dict]):

    return [
        {
            "role": "system",
            "content": LANGUAGE_ENFORCEMENT_MESSAGE
        },
        *messages
    ]


def build_mcp_explanation_messages(
    question: Question,
    tool_name: str,
    mcp_result,
):

    return [

        {
            "role": "system",
            "content": """
You are DeTLeng Analytics AI.

You explain verified analytics data returned from the internal Business Intelligence system.

Never invent numbers.

Never add categories, products, customers, sellers, metrics, or KPIs that are not present in the provided analytics data.

Preserve numeric values exactly as returned.

Explain the analytics in simple business language.

Provide useful insights and recommendations.

Reply in the user's language.
"""
        },

        {
            "role": "user",
            "content": f"""
User Question

{question.message}


MCP Tool

{tool_name}


Verified Analytics Data

{mcp_result}

Explain only these verified analytics results to the user.
"""
        }

    ]

# ==============================
# ROUTER HELPERS
# ==============================

def needs_mcp(question: str):

    intent, route = route_question(question)

    return intent == Intent.BUSINESS_KPI and route is not None


def select_mcp_tool(question: str):

    intent, route = route_question(question)

    if intent == Intent.BUSINESS_KPI and route is not None:
        return route.tool_name

    return None


def count_rows(result) -> int:

    if isinstance(result, list):
        return len(result)

    if isinstance(result, dict):
        return 1

    if result is None:
        return 0

    return 1


def log_router_debug(
    question: str,
    intent: Intent,
    tool_name: str | None,
    mcp_status: str | None = None,
    rows_returned: int | None = None,
    llm_status: str | None = None,
    action: str | None = None,
    returned: str | None = None,
    reason: str | None = None,
):

    if not DEBUG_ROUTER:
        return

    lines = [
        "=" * 40,
        "",
        f"Question:\n{question}",
        "",
        f"Intent:\n{intent.value}",
        "",
        f"Tool:\n{tool_name or 'NONE'}",
    ]

    if mcp_status is not None:
        lines.extend(["", f"MCP:\n{mcp_status}"])

    if rows_returned is not None:
        lines.extend(["", f"Rows Returned:\n{rows_returned}"])

    if llm_status is not None:
        lines.extend(["", f"LLM:\n{llm_status}"])

    if reason is not None:
        lines.extend(["", f"Reason:\n{reason}"])

    if action is not None:
        lines.extend(["", f"Action:\n{action}"])

    if returned is not None:
        lines.extend(["", f"Returned:\n{returned}"])

    lines.extend(["", "=" * 40])

    logger.info("\n".join(lines))


def error_response(answer: str):

    return {

        "status": "error",
        "answer": answer

    }


def success_response(source: str, answer: str):

    return {

        "status": "success",
        "source": source,
        "answer": answer

    }

# ==============================
# CHAT
# ==============================

@app.post("/chat")
def chat(question: Question):

    logger.info("Incoming chat question: %s", question.message)
    logger.info("Conversation history length: %s", len(question.history))

    intent, route = route_question(question.message)
    tool_name = route.tool_name if route else None

    logger.info("Intent classified: %s", intent.value)
    logger.info("Mapped MCP tool: %s", tool_name)

    # =====================================
    # TOOL DISCOVERY PATH
    # =====================================

    if intent == Intent.TOOL_DISCOVERY:

        try:

            tool_catalog = asyncio.run(
                get_tool_catalog(mcp)
            )

            answer = build_tool_catalog_answer(tool_catalog)

            log_router_debug(
                question=question.message,
                intent=intent,
                tool_name=None,
            mcp_status="SUCCESS",
            rows_returned=sum(len(tools) for tools in tool_catalog.values()),
            llm_status="NOT USED",
            action="Returned MCP registry.list_tools()",
        )

            return success_response("mcp_registry", answer)

        except Exception as e:

            logger.exception(
                "Tool discovery failed: question=%s error_type=%s error=%s",
                question.message,
                type(e).__name__,
                e,
            )

            return error_response(
                str(e)
            )

    # =====================================
    # DATASET INFORMATION PATH
    # =====================================

    if intent == Intent.DATASET_INFORMATION:

        try:

            dataset_info = asyncio.run(
                get_dataset_information(mcp)
            )

            answer = build_dataset_answer(dataset_info)

            log_router_debug(
                question=question.message,
                intent=intent,
                tool_name="server_status",
                mcp_status="SUCCESS",
                rows_returned=1,
                llm_status="NOT USED",
                action="Returned configured MCP dataset information",
            )

            return success_response("mcp", answer)

        except Exception as e:

            logger.exception(
                "Dataset information lookup failed: question=%s error_type=%s error=%s",
                question.message,
                type(e).__name__,
                e,
            )

            return error_response(
                str(e)
            )

    # =====================================
    # BUSINESS KPI PATH
    # =====================================

    if intent == Intent.BUSINESS_KPI:

        if route is None:

            logger.warning(
                "Business KPI intent has no registered MCP tool: question=%s",
                question.message,
            )

            log_router_debug(
                question=question.message,
                intent=intent,
                tool_name=None,
                mcp_status="NOT CALLED",
                llm_status="NOT USED",
                reason="No registered MCP tool",
                action="No MCP Tool Registered",
                returned=KPI_NOT_AVAILABLE_MESSAGE,
            )

            return error_response(KPI_NOT_AVAILABLE_MESSAGE)

        try:

            logger.info(
                "Executing deterministic MCP tool: tool=%s intent=%s question=%s",
                route.tool_name,
                intent.value,
                question.message,
            )

            mcp_result = asyncio.run(
                execute_mcp_tool(
                    mcp,
                    route,
                )
            )

            logger.info(
                "MCP response received: tool=%s rows=%s response=%r",
                route.tool_name,
                count_rows(mcp_result),
                mcp_result,
            )

        except Exception as e:

            logger.exception(
                "Deterministic MCP execution failed: tool=%s question=%s error_type=%s error=%s",
                route.tool_name,
                question.message,
                type(e).__name__,
                e,
            )

            log_router_debug(
                question=question.message,
                intent=intent,
                tool_name=route.tool_name,
                mcp_status="ERROR",
                llm_status="NOT USED",
                returned=f"{type(e).__name__}: {str(e)}",
            )

            return error_response(
                f"MCP error: {type(e).__name__}: {str(e)}"
            )

        messages = enforce_language_policy(
            build_mcp_explanation_messages(
                question,
                route.tool_name,
                mcp_result,
            )
        )

        try:

            logger.info(
                "Calling OpenAI for verified MCP result formatting only: model=%s tool=%s",
                OPENAI_MODEL,
                route.tool_name,
            )

            response = client.chat.completions.create(

                model=OPENAI_MODEL,

                messages=messages

            )

            answer = response.choices[0].message.content

            logger.info(
                "OpenAI formatting response received: tool=%s answer=%r",
                route.tool_name,
                answer,
            )

            log_router_debug(
                question=question.message,
                intent=intent,
                tool_name=route.tool_name,
                mcp_status="SUCCESS",
                rows_returned=count_rows(mcp_result),
                llm_status="Formatting Only",
            )

            return success_response("mcp", answer)

        except Exception as e:

            logger.exception(
                "OpenAI formatting failed after successful MCP response: tool=%s question=%s mcp_response=%r error_type=%s error=%s",
                route.tool_name,
                question.message,
                mcp_result,
                type(e).__name__,
                e,
            )

            return error_response(
                f"OpenAI formatting error: {type(e).__name__}: {str(e)}"
            )

    # =====================================
    # KNOWLEDGE / TECHNOLOGY / CASE STUDY / GENERAL PATH
    # =====================================

    try:

        logger.info(
            "Routing to knowledge path: intent=%s question=%s",
            intent.value,
            question.message,
        )

        messages = enforce_language_policy(
            build_messages(question)
        )

        logger.info(
            "Calling OpenAI for knowledge response: model=%s intent=%s",
            OPENAI_MODEL,
            intent.value,
        )

        response = client.chat.completions.create(

            model=OPENAI_MODEL,

            messages=messages

        )

        answer = response.choices[0].message.content

        logger.info(
            "OpenAI response received for knowledge path: intent=%s answer=%r",
            intent.value,
            answer,
        )

        log_router_debug(
            question=question.message,
            intent=intent,
            tool_name=None,
            mcp_status="NOT CALLED",
            llm_status="Knowledge Answer",
        )

        return success_response("knowledge", answer)

    except Exception as e:

        logger.exception(
            "Knowledge path OpenAI call failed with full traceback: intent=%s question=%s error_type=%s error=%s",
            intent.value,
            question.message,
            type(e).__name__,
            e,
        )

        return error_response(
            f"Knowledge response error: {type(e).__name__}: {str(e)}"
        )


# ==============================
# CHAT V2
# ==============================

@app.post("/chat-v2")
def chat_v2(question: Question):

    return chat(question)
