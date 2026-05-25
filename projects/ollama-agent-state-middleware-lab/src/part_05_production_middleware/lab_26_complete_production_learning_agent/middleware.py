from src.part_05_production_middleware.lab_22_tool_authorisation_middleware.middleware import (
    ToolAuthorisationMiddleware,
)
from src.part_05_production_middleware.lab_23_error_handling_middleware.middleware import (
    handle_tool_errors,
)
from src.part_05_production_middleware.lab_24_message_trimming_middleware.middleware import (
    MessageTrimmingMiddleware,
)
from src.part_05_production_middleware.lab_25_logging_middleware.middleware import (
    LoggingMiddleware,
)


def production_middleware():
    return [
        MessageTrimmingMiddleware(max_messages=6),
        LoggingMiddleware(),
        ToolAuthorisationMiddleware(),
        handle_tool_errors,
    ]
