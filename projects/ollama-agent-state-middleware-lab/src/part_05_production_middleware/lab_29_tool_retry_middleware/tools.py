from langchain.tools import tool


class FlakyCounter:
    def __init__(self) -> None:
        self.calls = 0

    def reset(self) -> None:
        self.calls = 0


_flaky_counter = FlakyCounter()


@tool
def flaky_tool() -> str:
    """
    Simulate a tool that fails twice, then succeeds.

    Intended for demonstrating retry middleware.
    """
    _flaky_counter.calls += 1
    if _flaky_counter.calls <= 2:
        raise RuntimeError(f"Temporary failure (call {_flaky_counter.calls})")
    return "Flaky tool succeeded on attempt 3."

