from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage


class ToolCallLimitMiddleware(AgentMiddleware):
    """
    Stop runaway tool-calling loops by enforcing a max tool-call budget.

    This is a pragmatic "execution recursion limit" for local-first agents:
    once the budget is exhausted, further tool calls are blocked and the model
    must finalize using existing context.
    """

    def __init__(self, max_tool_calls: int = 5):
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
                    "STOP: recursion / tool-call limit reached.\n"
                    f"Limit: {self.max_tool_calls} tool call(s) per request.\n"
                    f"Blocked tool: {tool_name}\n"
                    "Tell the user the agent hit an execution safety limit.\n"
                    "Do not call any more tools.\n"
                    "Give the best possible final answer with the current information."
                ),
                tool_call_id=request.tool_call["id"],
            )

        return handler(request)

