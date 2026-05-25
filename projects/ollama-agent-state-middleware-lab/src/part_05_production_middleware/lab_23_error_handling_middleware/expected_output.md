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
1. **Decorator Function**: `my_decorator` takes a function (`func`) and returns a new function (`wrapper`) that adds extra behavior.
2. **`@` Syntax**: The `@my_decorator` line applies the decorator to `say_hello()`.
3. **No Code Changes**: The original `say_hello()` doesn't need to know about the decorator.

### Common Uses:
- Logging (e.g., tracking when a function runs)
- Access control (e.g., checking permissions)
- Caching (e.g., memoizing results)

Decorators are like "superpowers" for functions—they let you add features cleanly and reuse code! 🦸‍♂️


Broken Tool Is Handled Safely
=============================

USER:
Use broken_quiz_generator for Python decorators

TOOL:
The tool 'broken_quiz_generator' failed safely.
Reason: Quiz service is temporarily unavailable
Please try again with a clearer learning request.

ASSISTANT:
It seems the quiz generation service is currently unavailable. While I can't generate quizzes right now, I can help explain Python decorators in simple terms. Would you like me to provide a clear explanation of decorators and their use cases?


What Changed?
=============
This lab adds error-handling middleware:
- Normal tools still run as before
- Tool exceptions are caught by middleware
- Failed tools return a safe ToolMessage instead of crashing the agent
- The agent can continue and explain the failure to the learner

Lab 24 will add message trimming middleware.