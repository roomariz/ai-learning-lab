from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage


@wrap_tool_call
def handle_tool_errors(request, handler):
    """Catch tool errors and return a safe ToolMessage."""

    tool_name = request.tool_call["name"]

    try:
        return handler(request)
    except Exception as exc:
        return ToolMessage(
            content=(
                f"The tool '{tool_name}' failed safely.\n"
                f"Reason: {str(exc)[:120]}\n"
                "Tell the user the request failed safely.\n"
                "Do not offer alternatives.\n"
                "Do not invent a replacement workflow."
            ),
            tool_call_id=request.tool_call["id"],
        )
