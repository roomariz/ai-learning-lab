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
                    "BLOCKED: premium feature.\n"
                    "This tool requires premium access.\n"
                    "Tell the user this feature requires premium access.\n"
                    "Do not offer alternatives.\n"
                    "Do not suggest substitute tools.\n"
                    "Do not recreate the blocked functionality."
                ),
                tool_call_id=request.tool_call["id"],
            )

        return handler(request)
