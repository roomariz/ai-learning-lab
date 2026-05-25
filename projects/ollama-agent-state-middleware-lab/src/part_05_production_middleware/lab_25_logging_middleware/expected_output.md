25 Logging Middleware
=====================

USER:
Explain Python decorators
[log] 2026-05-25 14:53:04 agent started
[log] model input messages (pre-model state): 1
[log] tool started: explain_topic
[log] tool finished: explain_topic
[log] model input messages (pre-model state): 3
[log] 2026-05-25 14:55:06 agent finished
[log] final message count: 4

TOOL:
Python decorators: explanation with simple concepts and examples.

ASSISTANT:
Python decorators are a way to **add functionality to existing functions** without modifying their code. Think of them as "wrappers" that surround a function, letting you enhance its behavior before or after it runs.

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
2. **`wrapper()`** is a nested function that adds extra logic (e.g., logging, validation) and calls the original function.
3. The **`@my_decorator`** syntax is shorthand for `say_hello = my_decorator(say_hello)`.

### Common Uses:
- Logging (e.g., tracking when a function runs)
- Access control (e.g., checking permissions)
- Timing functions (e.g., measuring execution speed)

Decorators are powerful because they let you keep code clean and reusable! 🚀


USER:
Generate a practice question about Python decorators
[log] 2026-05-25 14:55:06 agent started
[log] model input messages (pre-model state): 1
[log] tool started: generate_practice_question
[log] tool finished: generate_practice_question
[log] model input messages (pre-model state): 3
[log] 2026-05-25 14:57:34 agent finished
[log] final message count: 4

TOOL:
Practice question for Python decorators: Write a decorator called `log_call` that prints the wrapped function's name before calling it. Apply it to a function called `add(a, b)` and show the expected output.

ASSISTANT:
Here's the solution:

```python
# Define the decorator
def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        return result
    return wrapper

# Apply decorator to a function
@log_call
def add(a, b):
    return a + b

# Test the decorated function
add(3, 4)
```

**Expected Output:**
```
Calling add
7
```

**Explanation:**  
The decorator `log_call` wraps the `add` function. When `add(3,4)` is called:  
1. It first prints "Calling add"  
2. Then executes the original function logic (3 + 4)  
3. Returns the result (7)


What Changed?
=============
This lab adds logging middleware:
- Logs agent start/finish timestamps
- Logs model input message count
- Logs tool start/finish events

Lab 26 will compose multiple middleware layers into a production agent.