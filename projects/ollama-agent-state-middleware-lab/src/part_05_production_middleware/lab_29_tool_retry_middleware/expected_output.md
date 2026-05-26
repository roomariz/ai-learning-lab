29 Tool Retry Middleware
========================
Goal: recover from transient tool failures.
Demo tool: fails twice, succeeds on third attempt.
Middleware: retries before returning a safe error.


USER:
Call flaky_tool now and return its result. Do not do anything else.
[retry] attempt 2/3: flaky_tool
[retry] attempt 3/3: flaky_tool

TOOL:
Flaky tool succeeded on attempt 3.

ASSISTANT:
The flaky tool succeeded on attempt 3.