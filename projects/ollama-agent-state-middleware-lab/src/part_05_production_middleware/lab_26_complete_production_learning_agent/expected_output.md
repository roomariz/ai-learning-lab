26 Complete Production Learning Agent (Capstone)
================================================

Scenario 1: normal request
==========================

USER:
Explain Python decorators
[log] 2026-05-25 14:20:58 agent started
[log] model input messages (pre-model state): 1
[log] tool started: explain_topic
[log] tool finished: explain_topic
[log] model input messages (pre-model state): 3
[log] 2026-05-25 14:21:53 agent finished
[log] final message count: 4

TOOL:
Python decorators: explanation with simple concepts and examples.

ASSISTANT:
Python decorators are a way to modify or enhance functions **without changing their original code**. Think of them as special "wrappers" that add functionality before or after a function runs.

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
1. **`@my_decorator`** applies the decorator to `say_hello()`.
2. The decorator `my_decorator` takes the original function `func` as input.
3. The `wrapper()` function adds extra behavior (printing messages) and calls the original function.

### Common Uses:
- Logging (e.g., tracking when a function runs)
- Access control (e.g., checking permissions)
- Timing functions (e.g., measuring execution speed)

Decorators are like "superpowers" for functions—they let you add features cleanly without rewriting the original code! 🦸‍♂️


Scenario 2: premium blocked
===========================

USER:
Create a 7 day study plan for Python decorators
[log] 2026-05-25 14:21:53 agent started
[log] model input messages (pre-model state): 1
[log] tool started: create_study_plan
[log] tool finished: create_study_plan
[log] model input messages (pre-model state): 3
[log] 2026-05-25 14:22:09 agent finished
[log] final message count: 4

TOOL:
BLOCKED: premium feature.
This tool requires premium access.
Tell the user this feature requires premium access.
Do not offer alternatives.
Do not suggest substitute tools.
Do not recreate the blocked functionality.

ASSISTANT:
The create_study_plan tool requires premium access to generate a customized study schedule. Unfortunately, I cannot assist with this request without premium permissions.


Scenario 3: tool failure
========================

USER:
Use broken_quiz_generator for Python decorators
[log] 2026-05-25 14:22:09 agent started
[log] model input messages (pre-model state): 1
[log] tool started: broken_quiz_generator
[log] tool finished: broken_quiz_generator
[log] model input messages (pre-model state): 3
[log] 2026-05-25 14:22:27 agent finished
[log] final message count: 4

TOOL:
The tool 'broken_quiz_generator' failed safely.
Reason: Quiz service is temporarily unavailable
Tell the user the request failed safely.
Do not offer alternatives.
Do not invent a replacement workflow.

ASSISTANT:
The request to generate a quiz using the broken_quiz_generator failed safely. The reason provided was: "Quiz service is temporarily unavailable." No further action or alternatives were offered.


Scenario 4: long history (trimming)
===================================

MESSAGES:
7 total
[log] 2026-05-25 14:22:27 agent started
[trim] reduced messages from 7 to 6
[log] model input messages (pre-model state): 7
[log] 2026-05-25 14:23:22 agent finished
[log] final message count: 8

ASSISTANT:
Decorators in Python are a way to modify or enhance functions (or classes) without changing their original code. They act like "wrappers" that add functionality before or after the function runs. Think of them as a special syntax (`@decorator`) that lets you attach behavior to functions easily.

### Example:
```python
def my_decorator(func):
    def wrapper():
        print("Before function call")
        func()  # Call the original function
        print("After function call")
    return wrapper

@my_decorator
def say_hello():
    print("Hello")

say_hello()
```

**Output:**
```
Before function call
Hello
After function call
```

### Key Concepts:
1. **Decorators are functions** that take another function as input.
2. They return a "wrapper" function that adds extra logic (e.g., logging, timing, access control).
3. The `@decorator` syntax is shorthand for `function = decorator(function)`.

Common uses include logging, authentication, caching, and validating inputs. Would you like a practice question to test your understanding? 😊


What Changed?
=============
This capstone composes four production middleware layers:
- Logging (visibility into lifecycle)
- Message trimming (bounded context)
- Tool authorisation (premium controls)
- Error handling (safe tool failures)

Part 05 is complete.
