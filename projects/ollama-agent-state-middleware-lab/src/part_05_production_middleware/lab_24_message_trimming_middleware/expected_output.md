24 Message Trimming Middleware
==============================

Example 1: Final User Request Survives
======================================
max_messages=3 keeps the latest 3 messages.
The first five messages are removed.
The final user request remains, so the agent can answer.


MESSAGES:
8 total
[trim] reduced messages from 8 to 3

ASSISTANT:
Decorators in Python are a way to modify or enhance functions **without changing their code**. Think of them as special "wrappers" that add functionality to existing functions. They are defined using the `@` symbol followed by the decorator's name.

### How They Work:
1. A decorator is itself a function that takes another function as input.
2. It returns a new function that wraps the original one, adding extra behavior (like logging, timing, or authentication).
3. The `@decorator` syntax is shorthand for wrapping the function.

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
    print("Hello!")

say_hello()
```

### Output:
```
Before function call
Hello!
After function call
```

### Key Use Cases:
- Logging: Track when a function is called.
- Timing: Measure how long a function takes to run.
- Authentication: Check if a user is logged in before executing a function.

Decorators make code cleaner by separating concerns (e.g., keeping business logic separate from logging).


Example 2: No Fresh User Request
================================
max_messages=3 keeps the latest 3 messages.
The real request about decorators is removed.
The remaining input contains only placeholder messages.
The agent may produce an empty or confusing response.


MESSAGES:
6 total
[trim] reduced messages from 6 to 3

ASSISTANT:
[no response]


Why Order Matters
=================
If the last message is an assistant message, the agent may have no fresh user request.
That can produce an empty or confusing response.

Correct pattern:
- old user message
- old assistant response
- latest user request

Avoid ending the input with an old assistant response.

What Changed?
=============
This lab adds message trimming middleware:
- Large message histories are cut down before the model runs
- Old messages at the top are removed first
- Recent messages at the bottom are kept
- The final user request should normally be the last message
- If the final user request is trimmed away, the agent may not know what to answer
- The agent remains functional while context stays bounded

Lab 25 will add logging middleware.