# CHANGELOG

## Final Hardening - Deterministic AI Business Intelligence Platform

This release hardens the DeTLeng AI Business Intelligence platform so Business Intelligence questions are routed deterministically through Python and MCP, while OpenAI is used only for knowledge responses or verified-result explanation.

---

## Files Changed

### casestudy-ai-backend/main.py

Updated the request orchestration layer.

Changes:

- Added deterministic handling for tool discovery.
- Added deterministic handling for dataset and server-status questions.
- Ensured `TOOL_DISCOVERY`, `DATASET_INFORMATION`, and server-status routes never call OpenAI.
- Added Python-side language enforcement before every OpenAI completion request.
- Kept `/chat` and `/chat-v2` API responses compatible with the frontend.
- Preserved OpenAI usage for knowledge, technology, case-study, and verified MCP result explanation only.

Reason:

Business KPI and platform metadata questions must not depend on LLM judgment. The backend now decides the route before any OpenAI call.

---

### casestudy-ai-backend/registry.py

Updated the deterministic intent registry.

Changes:

- Added tool-discovery phrase coverage for `List available MCP tools`.
- Added server-status phrases to dataset/platform metadata routing.
- Preserved deterministic classification into:
  - `BUSINESS_KPI`
  - `TOOL_DISCOVERY`
  - `DATASET_INFORMATION`
  - `TECHNOLOGY`
  - `KNOWLEDGE`
  - `CASE_STUDY`
  - `GENERAL`
- Preserved MCP tool mapping for KPI routes.

Reason:

Tool discovery and dataset/server-status questions must be routed before technology or knowledge fallback.

---

### casestudy-ai-backend/executor.py

Updated MCP execution helpers.

Changes:

- Tool discovery now calls the MCP server's `list_registered_tools` tool.
- Tool discovery formats only the returned MCP registry tool names.
- Dataset information continues to call `server_status`.
- Dataset status formatting now returns a clean business-readable status.

Reason:

The MCP registry must remain the single source of truth for available Business Intelligence tools.

---

### casestudy-ai-backend/mcp_client.py

Updated MCP client discovery and validation.

Changes:

- Tool validation uses live MCP server discovery instead of a hardcoded backend list.
- Preserved `await mcp.call_tool(tool_name, arguments)` public API.
- Preserved retry, timeout, response extraction, and detailed logging behavior.

Reason:

The backend should not maintain a duplicated static tool list. The MCP server registry is authoritative.

---

### detleng-bigquery-mcp/registry.py

Updated the MCP server registry.

Changes:

- Added `list_tools()` to return all registered Business Intelligence tool names from `TOOL_REGISTRY`.

Reason:

The server-side registry is now explicitly queryable and remains the single source of truth.

---

### detleng-bigquery-mcp/executor.py

Updated the MCP server executor.

Changes:

- Added `list_registered_tools()` to expose registry tool names through a clean executor function.

Reason:

Tool discovery is now handled through the same registry/executor pattern as tool execution.

---

### detleng-bigquery-mcp/server.py

Updated the MCP server registration layer.

Changes:

- Added `list_registered_tools` MCP tool.
- This tool returns `registry.list_tools()` through the executor.
- Existing MCP tools and public tool names remain unchanged.

Reason:

The backend can now ask the MCP server for the actual registered Business Intelligence tools without using OpenAI or hardcoded backend lists.

---

## Deterministic Routing

The backend now follows this route order:

1. User question arrives at FastAPI.
2. Python intent router classifies the request.
3. Tool discovery requests call MCP `list_registered_tools`.
4. Dataset/server-status requests call MCP `server_status`.
5. Business KPI requests use a mapped MCP tool when available.
6. Unknown KPI requests return:

```text
This KPI is currently not available through the Business Intelligence layer.
```

7. OpenAI is used only for:
   - Explaining verified MCP results
   - Technology questions
   - Knowledge Base questions
   - Case study questions
   - General non-KPI responses

OpenAI no longer decides whether MCP should be called.

---

## Language Enforcement

Before every OpenAI completion request, the backend now injects a system instruction:

```text
You MUST answer in English unless the user explicitly requests another language.

Never infer language from dataset values, product names, customer names, country names, or business data.

If the user explicitly asks for another language, use only that requested language.
```

This is enforced in Python and does not rely only on the system prompt.

Routes that do not use OpenAI, such as tool discovery and dataset information, are formatted directly by Python.

---

## Deterministic Non-OpenAI Routes

These routes never use OpenAI:

- `List available MCP tools`
- `List available tools`
- `What tools do you have?`
- `Which dataset are you using?`
- `Server status`

They are handled by Python and MCP only.

---

## Additional Improvements

- Tool discovery now returns only MCP-registered Business Intelligence tools.
- Dataset information now comes directly from MCP `server_status`.
- MCP server registry now exposes a clean `list_tools()` function.
- Backend MCP client no longer depends on a duplicated hardcoded allow-list.

---

## Recommendations

- Keep adding future MCP tools only to the MCP server registry.
- Keep backend routing keywords aligned with user-facing business language.
- Add automated tests from `ROUTING_TEST.md` to CI.
- Keep `DEBUG_ROUTER=true` enabled in staging for fast routing diagnostics.
