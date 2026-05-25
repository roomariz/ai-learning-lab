26 Complete Production Learning Agent (Capstone)
================================================

Scenario 1: normal request
==========================

USER:
Explain Python decorators
[log] 2026-05-25 14:57:42 agent started
[log] model input messages (pre-model state): 1
[log] tool started: explain_topic
[log] tool finished: explain_topic
[log] model input messages (pre-model state): 3
[log] 2026-05-25 15:00:13 agent finished
[log] final message count: 4

TOOL:
Python decorators: explanation with simple concepts and examples.

ASSISTANT:
Python decorators are a way to modify or enhance functions without changing their code. They act like "wrappers" that add functionality before or after a function runs. Here's a simple example:

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before function call")
        result = func(*args, **kwargs)
        print("After function call")
        return result
    return wrapper

@my_decorator
def add(a, b):
    return a + b

add(3, 5)
```

**Output:**
```
Before function call
After function call
8
```

### Key Concepts:
1. `my_decorator` is a function that takes another function `func` as input.
2. The `wrapper` function contains the code to run before/after the original function.
3. The `@my_decorator` syntax applies the decorator to the `add` function.
4. When `add(3, 5)` is called, it actually calls the `wrapper` function.

Decorators are commonly used for logging, access control, caching, and more. They allow you to add behavior to existing functions without modifying their code directly.


Scenario 2: premium blocked
===========================
Expect: ToolAuthorisationMiddleware returns a ToolMessage; premium tool does not run.


USER:
Create a 7 day study plan for Python decorators
[log] 2026-05-25 15:00:13 agent started
[log] model input messages (pre-model state): 1
[log] tool started: create_study_plan
[log] tool finished: create_study_plan
[log] model input messages (pre-model state): 3
[log] 2026-05-25 15:00:46 agent finished
[log] final message count: 4

TOOL:
BLOCKED: premium feature.
This tool requires premium access.
Tell the user this feature requires premium access.
Do not offer alternatives.
Do not suggest substitute tools.
Do not recreate the blocked functionality.

ASSISTANT:
I'm unable to create a study plan as this functionality requires premium access. Would you like me to help with something else?


Scenario 3: tool failure
========================
Expect: error middleware catches the failing tool and returns a safe ToolMessage.


USER:
Use broken_quiz_generator for Python decorators
[log] 2026-05-25 15:00:46 agent started
[log] model input messages (pre-model state): 1
[log] tool started: broken_quiz_generator
[log] tool finished: broken_quiz_generator
[log] model input messages (pre-model state): 3
[log] 2026-05-25 15:01:19 agent finished
[log] final message count: 4

TOOL:
The tool 'broken_quiz_generator' failed safely.
Reason: Quiz service is temporarily unavailable
Tell the user the request failed safely.
Do not offer alternatives.
Do not invent a replacement workflow.

ASSISTANT:
The request to generate a quiz using the broken_quiz_generator failed safely. The reason provided was: "Quiz service is temporarily unavailable."


Scenario 4: long history (trimming)
===================================

MESSAGES:
7 total
[log] 2026-05-25 15:01:19 agent started
[trim] reduced messages from 7 to 6
[log] model input messages (pre-model state): 7
[log] tool started: explain_topic
[log] tool finished: explain_topic
[trim] reduced messages from 9 to 6
[log] model input messages (pre-model state): 9
[log] 2026-05-25 15:03:11 agent finished
[log] final message count: 10

ASSISTANT:
Python decorators are like special "wrappers" around functions that add extra functionality without modifying the original function's code. Think of them as a way to *enhance* or *modify* how a function behaves, such as adding logging, timing, or access control.

### Simple Example:
```python
def my_decorator(func):
    def wrapper():
        print("Before function call")
        func()  # Call the original function
        print("After function call")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
```

### Output:
```
Before function call
Hello!
After function call
```

### Key Concepts:
1. **`my_decorator`** is a function that takes another function (`func`) as input.
2. **`wrapper()`** is a nested function that adds behavior (e.g., printing messages) before and after the original function.
3. The **`@my_decorator`** syntax applies the decorator to `say_hello()`.

### Common Uses:
- Logging (e.g., tracking when a function runs)
- Access control (e.g., checking permissions)
- Caching (e.g., memoizing results)

Decorators are powerful because they let you extend functionality cleanly without rewriting code! 🚀


What Changed?
=============
This capstone composes four production middleware layers:
- Logging (visibility into lifecycle)
- Message trimming (bounded context)
- Tool authorisation (premium controls)
- Error handling (safe tool failures)

Part 05 is complete.