from __future__ import annotations

import time

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage


class ToolRetryMiddleware(AgentMiddleware):
    """Retry transient tool failures before returning a safe error."""

    def __init__(
        self,
        max_attempts: int = 3,
        backoff_seconds: float = 0.0,
    ):
        super().__init__()
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if backoff_seconds < 0:
            raise ValueError("backoff_seconds must be >= 0")

        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds

    def wrap_tool_call(self, request, handler):
        tool_name = request.tool_call["name"]

        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                if attempt > 1:
                    print(f"[retry] attempt {attempt}/{self.max_attempts}: {tool_name}")
                return handler(request)
            except Exception as exc:
                last_error = exc
                if attempt >= self.max_attempts:
                    break
                if self.backoff_seconds:
                    time.sleep(self.backoff_seconds)

        return ToolMessage(
            content=(
                f"The tool '{tool_name}' failed after {self.max_attempts} attempt(s).\n"
                f"Last error: {str(last_error)[:160] if last_error else 'unknown'}\n"
                "Tell the user the tool failed temporarily and could not recover.\n"
                "Do not call any more tools.\n"
                "Do not invent a replacement workflow."
            ),
            tool_call_id=request.tool_call["id"],
        )

