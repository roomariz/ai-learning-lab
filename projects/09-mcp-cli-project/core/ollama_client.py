import httpx


class Claude:
    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.client = httpx.Client(timeout=120.0)

    def add_user_message(self, messages: list, message):
        messages.append({
            "role": "user",
            "content": getattr(message, "content", message),
        })

    def add_assistant_message(self, messages: list, message):
        if isinstance(message, dict):
            message_content = message.get("message", {})
            content = message_content.get("content", "")
            assistant_message = {
                "role": "assistant",
                "content": content,
            }
            if "tool_calls" in message_content:
                assistant_message["tool_calls"] = message_content["tool_calls"]
            messages.append(assistant_message)
            return
        else:
            content = getattr(message, "content", message)

        messages.append({
            "role": "assistant",
            "content": content,
        })

    def text_from_message(self, message):
        if isinstance(message, dict):
            return message["message"]["content"]
        return getattr(message, "content", str(message))

    def chat(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop_sequences=None,
        tools=None,
        thinking=False,
        thinking_budget=1024,
    ):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        if system:
            messages = [{"role": "system", "content": system}] + messages

        if stop_sequences:
            payload["options"]["stop"] = stop_sequences

        # Ollama tool calling support (if model supports it)
        if tools:
            payload["tools"] = tools

        response = self.client.post(
            f"{self.base_url}/api/chat",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def close(self):
        self.client.close()
