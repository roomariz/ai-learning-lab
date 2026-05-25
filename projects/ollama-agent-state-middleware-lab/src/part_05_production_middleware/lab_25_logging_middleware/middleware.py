from datetime import datetime

from langchain.agents.middleware import AgentMiddleware


class LoggingMiddleware(AgentMiddleware):
    """Log important agent lifecycle events."""

    def before_agent(self, state, runtime):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[log] {timestamp} agent started")
        return None

    def before_model(self, state, runtime):
        messages = state.get("messages", [])
        print(f"[log] model input messages (pre-model state): {len(messages)}")
        return None
    
    def wrap_tool_call(self, request, handler):
        tool_name = request.tool_call["name"]
        print(f"[log] tool started: {tool_name}")

        result = handler(request)

        print(f"[log] tool finished: {tool_name}")
        return result

    def after_agent(self, state, runtime):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messages = state.get("messages", [])
        print(f"[log] {timestamp} agent finished")
        print(f"[log] final message count: {len(messages)}")
        return None
