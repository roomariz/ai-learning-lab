from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage


class ToolAuthorisationMiddleware(AgentMiddleware):
    """Block premium tools for non-premium learners."""

    def __init__(self, user_tier: str = "free"):
        super().__init__()
        self.user_tier = user_tier
        self.premium_tools = {"grade_answer", "create_study_plan"}

    def wrap_tool_call(self, request, handler):
        tool_name = request.tool_call["name"]

        if tool_name in self.premium_tools and self.user_tier != "premium":
            return ToolMessage(
                content=(
                    f"BLOCKED: '{tool_name}' is unavailable.\n"
                    "This tool requires premium access.\n"
                    "Do not offer to recreate the same premium feature using other tools.\n"
                    "Tell the user that premium access is required."
                ),
                tool_call_id=request.tool_call["id"],
            )

        return handler(request)

