28 Rate Limiting Middleware
===========================
Goal: limit tool calls per request.
Config: max_tool_calls=1
Expect: first tool call allowed, second tool call blocked.


USER:
Explain Python decorators using explain_topic, then create a 7-day study plan using create_study_plan.

TOOL:
Python decorators: explanation with simple concepts and examples.

TOOL:
BLOCKED: tool call rate limit exceeded.
Limit: 1 tool call(s) per request.
Attempted tool: create_study_plan
Tell the user the request exceeded the tool-call limit.
Do not call any more tools.
Do not manually recreate blocked functionality.
Ask the user to split the request into smaller steps.

ASSISTANT:
I reached a tool call limit while processing your request. Please split this into two separate requests:
1. First, ask for an explanation of Python decorators
2. Then, ask for a 7-day Python study plan

This will allow me to handle each task individually within the tool call limits.