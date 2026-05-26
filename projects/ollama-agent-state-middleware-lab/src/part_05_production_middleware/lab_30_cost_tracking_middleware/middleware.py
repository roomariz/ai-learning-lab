from __future__ import annotations

import time

from langchain.agents.middleware import AgentMiddleware


class CostTrackingMiddleware(AgentMiddleware):
    """
    Track lightweight cost signals for local-first agents.

    This is intentionally heuristic. For local models, "cost" often means
    latency, memory, compute, and tool usage.
    """

    def __init__(self) -> None:
        super().__init__()
        self.started_at = 0.0
        self.message_count = 0
        self.tool_call_count = 0

    def before_agent(self, state, runtime):
        self.started_at = time.time()
        self.message_count = 0
        self.tool_call_count = 0
        print("[cost] request started")
        return None

    def before_model(self, state, runtime):
        messages = state.get("messages", [])
        self.message_count = len(messages)
        print(f"[cost] messages: {self.message_count}")
        return None

    def wrap_tool_call(self, request, handler):
        self.tool_call_count += 1
        return handler(request)

    def after_agent(self, state, runtime):
        elapsed_ms = int((time.time() - self.started_at) * 1000)
        category = self._estimate_local_cost_category(
            message_count=self.message_count,
            tool_call_count=self.tool_call_count,
            elapsed_ms=elapsed_ms,
        )
        print(f"[cost] tool calls: {self.tool_call_count}")
        print(f"[cost] elapsed_ms: {elapsed_ms}")
        print(f"[cost] estimated_local_compute_load: {category}")
        return None

    @staticmethod
    def _estimate_local_cost_category(
        *,
        message_count: int,
        tool_call_count: int,
        elapsed_ms: int,
    ) -> str:
        score = 0

        if message_count >= 12:
            score += 2
        elif message_count >= 6:
            score += 1

        if tool_call_count >= 4:
            score += 2
        elif tool_call_count >= 2:
            score += 1

        if elapsed_ms >= 25_000:
            score += 2
        elif elapsed_ms >= 7_500:
            score += 1

        if score >= 4:
            return "high"
        if score >= 2:
            return "medium"
        return "low"

