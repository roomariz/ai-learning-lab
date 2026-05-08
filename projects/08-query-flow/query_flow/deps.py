"""Shared dependency guards for optional QueryFlow features."""

from __future__ import annotations


def install_hint(extra: str | None = None) -> str:
    if extra:
        quoted = f'query-flow[{extra}]'
        return f'pip install "{quoted}"\nOr: uv pip install "{quoted}"'
    return 'pip install query-flow\nOr: uv pip install query-flow'


def require(dep: str, purpose: str, extra: str | None = None) -> None:
    raise ImportError(
        f"{dep} is required for {purpose}. Install with:\n{install_hint(extra)}"
    )
