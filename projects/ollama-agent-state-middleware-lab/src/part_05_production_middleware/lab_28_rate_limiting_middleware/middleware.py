from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage


class RateLimitingMiddleware(AgentMiddleware):
    """
    Limit total tool calls per agent request.

    This is a coarse but effective safety guard: even valid users should not be
    able to run unbounded tool chains in a single request.
    """

    def __init__(self, max_tool_calls: int = 3):
        super().__init__()
        self.max_tool_calls = max_tool_calls
        self.tool_call_count = 0

    def before_agent(self, state, runtime):
        self.tool_call_count = 0
        return None

    def wrap_tool_call(self, request, handler):
        self.tool_call_count += 1

        if self.tool_call_count > self.max_tool_calls:
            tool_name = request.tool_call["name"]

            return ToolMessage(
                content=(
                    "BLOCKED: tool call rate limit exceeded.\n"
                    f"Limit: {self.max_tool_calls} tool call(s) per request.\n"
                    f"Attempted tool: {tool_name}\n"
                    "Tell the user the request exceeded the tool-call limit.\n"
                    "Do not call any more tools.\n"
                    "Do not manually recreate blocked functionality.\n"
                    "Ask the user to split the request into smaller steps."
                ),
                tool_call_id=request.tool_call["id"],
            )

        return handler(request)

