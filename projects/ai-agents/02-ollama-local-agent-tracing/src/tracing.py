import json
import logging
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any
from uuid import uuid4


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "agent-trace.jsonl"
LOG_RETENTION_DAYS = 7


file_handler = TimedRotatingFileHandler(
    filename=LOG_FILE,
    when="midnight",
    interval=1,
    backupCount=LOG_RETENTION_DAYS,
    encoding="utf-8",
    utc=True,
)

file_handler.suffix = "%Y-%m-%d"

console_handler = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        file_handler,
        console_handler,
    ],
)

logger = logging.getLogger("agent_trace")


def log_event(
    trace_id: str,
    event_type: str,
    data: dict[str, Any],
) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": trace_id,
        "event_type": event_type,
        "data": data,
    }

    logger.info(json.dumps(event, ensure_ascii=False))


def _content_value(content: Any, redact_content: bool) -> Any:
    if redact_content:
        return "[REDACTED]"

    return content


def log_agent_trace(
    result: dict[str, Any],
    trace_id: str | None = None,
    redact_content: bool = False,
) -> str:
    trace_id = trace_id or str(uuid4())
    messages = result.get("messages", [])

    log_event(
        trace_id=trace_id,
        event_type="trace_started",
        data={"message_count": len(messages)},
    )

    for index, message in enumerate(messages, start=1):
        message_type = message.__class__.__name__

        if message_type == "HumanMessage":
            log_event(
                trace_id=trace_id,
                event_type="user_message",
                data={
                    "step": index,
                    "content": _content_value(message.content, redact_content),
                },
            )

        elif message_type == "AIMessage":
            tool_calls = getattr(message, "tool_calls", None)

            if tool_calls:
                for tool_call in tool_calls:
                    log_event(
                        trace_id=trace_id,
                        event_type="tool_call_requested",
                        data={
                            "step": index,
                            "tool_call_id": tool_call.get("id"),
                            "tool_name": tool_call.get("name"),
                            "tool_args": _content_value(
                                tool_call.get("args"),
                                redact_content,
                            ),
                        },
                    )
            else:
                log_event(
                    trace_id=trace_id,
                    event_type="final_answer",
                    data={
                        "step": index,
                        "content": _content_value(message.content, redact_content),
                    },
                )

        elif message_type == "ToolMessage":
            log_event(
                trace_id=trace_id,
                event_type="tool_observation",
                data={
                    "step": index,
                    "tool_call_id": getattr(message, "tool_call_id", None),
                    "tool_name": message.name,
                    "tool_output": _content_value(message.content, redact_content),
                },
            )

        else:
            log_event(
                trace_id=trace_id,
                event_type="unknown_message_type",
                data={
                    "step": index,
                    "message_type": message_type,
                    "content": _content_value(
                        getattr(message, "content", None),
                        redact_content,
                    ),
                },
            )

    log_event(
        trace_id=trace_id,
        event_type="trace_completed",
        data={"message_count": len(messages)},
    )

    return trace_id