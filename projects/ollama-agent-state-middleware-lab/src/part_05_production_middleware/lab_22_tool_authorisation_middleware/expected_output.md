22 Tool Authorisation Middleware
================================

Using invoke()
==============

USER:
Create a 7 day study plan for Python decorators

ASSISTANT:
I currently don't have access to create premium study plans. However, I can help you:

1. Explain Python decorators in simple terms
2. Generate practice questions about decorators
3. Grade your answers to those questions

Would you like me to help with any of these instead?
[time] invoke() took 21.08 seconds


Using stream()
==============

USER:
Create a 7 day study plan for Python decorators

TOOL:
BLOCKED: 'create_study_plan' is unavailable.
This tool requires premium access.
Do not offer to recreate the same premium feature using other tools.
Tell the user that premium access is required.

ASSISTANT:
I currently don't have access to create premium study plans. However, I can help you:

1. Explain Python decorators in simple terms
2. Generate practice questions about decorators
3. Grade your answers to those questions

Would you like me to help with any of these instead?
[time] stream() took 22.43 seconds


What Changed?
=============
This lab adds the first middleware layer:
- Free tools are allowed
- Premium tools are blocked for free users
- Tool access is now controlled outside the tool itself
- The agent can still reason, but middleware controls execution

Lab 23 will add error handling middleware.