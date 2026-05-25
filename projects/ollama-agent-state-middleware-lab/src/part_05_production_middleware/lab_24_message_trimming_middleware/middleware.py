from langchain.agents.middleware import AgentMiddleware


class MessageTrimmingMiddleware(AgentMiddleware):
    """Keep only the most recent messages before the model is called."""

    def __init__(self, max_messages: int = 6):
        super().__init__()
        self.max_messages = max_messages

    def before_model(self, state, runtime):
        messages = state.get("messages", [])

        if len(messages) <= self.max_messages:
            return None

        original_count = len(messages)
        trimmed_messages = messages[-self.max_messages:]

        print(
            f"[trim] reduced messages from "
            f"{original_count} to {len(trimmed_messages)}"
        )

        return {"messages": trimmed_messages}