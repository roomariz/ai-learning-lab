23 Error Handling Middleware
============================

Normal Tool Still Works
=======================

USER:
Explain Python decorators

TOOL:
Python decorators: explanation with simple concepts and examples.

ASSISTANT:
Python decorators are a way to **add functionality to existing functions** without modifying their code. Think of them as special "wrappers" that surround a function, letting you enhance its behavior automatically.

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
2. **`wrapper()`** is a nested function that adds extra behavior (like logging) before/after the original function.
3. The **`@my_decorator`** syntax applies the decorator to `say_hello()`.

### Common Uses:
- Logging (e.g., tracking when a function runs)
- Access control (e.g., checking permissions)
- Timing functions (e.g., measuring execution speed)
- Caching results (e.g., memoization)

Decorators are powerful because they let you **separate concerns**—adding features without "polluting" the original function's code. 🌟


Broken Tool Is Handled Safely
=============================

USER:
Use broken_quiz_generator for Python decorators

TOOL:
The tool 'broken_quiz_generator' failed safely.
Reason: Quiz service is temporarily unavailable
Tell the user the request failed safely.
Do not offer alternatives.
Do not invent a replacement workflow.

ASSISTANT:
The quiz service is temporarily unavailable, so I cannot generate a quiz at this time. Please try again later.


What Changed?
=============
This lab adds error-handling middleware:
- Normal tools still run as before
- Tool exceptions are caught by middleware
- Failed tools return a safe ToolMessage instead of crashing the agent
- The agent can continue and explain the failure to the learner

Lab 24 will add message trimming middleware.