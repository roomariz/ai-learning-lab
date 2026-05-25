25 Logging Middleware
=====================

USER:
Explain Python decorators
[log] 2026-05-25 13:50:07 agent started
[log] model input messages: 1
[log] tool started: explain_topic
[log] tool finished: explain_topic
[log] model input messages: 3
[log] 2026-05-25 13:50:38 agent finished
[log] final message count: 4

TOOL:
Python decorators: explanation with simple concepts and examples.

ASSISTANT:
Python decorators are a way to modify or enhance functions **without changing their code**. Think of them as special "wrappers" that add extra functionality to existing functions. They’re like a jacket you can put around a function to add features like logging, timing, or access control.

---

### 🧠 How They Work (Simplified)
1. **A decorator is a function** that takes another function as input.
2. It returns a **new function** that wraps the original one, adding behavior before or after the original function runs.
3. You use the `@` symbol to apply the decorator to a function.

---

### 📌 Example: A Simple Decorator
```python
def my_decorator(func):
    def wrapper():
        print("Before the function runs!")
        func()  # Call the original function
        print("After the function runs!")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
```

**Output:**
```
Before the function runs!
Hello!
After the function runs!
```

---

### 🚀 Key Use Cases
- **Logging**: Track when a function is called.
- **Timing**: Measure how long a function takes to run.
- **Access Control**: Restrict who can use a function.
- **Caching**: Store results of expensive function calls.

---

### 🧩 Why Use Decorators?
They keep code clean and reusable. Instead of writing repetitive code (e.g., logging inside every function), you can define a decorator once and apply it to multiple functions.

Would you like a coding practice question to test your understanding? 😊


USER:
Generate a practice question about Python decorators
[log] 2026-05-25 13:50:38 agent started
[log] model input messages: 1
[log] tool started: generate_practice_question
[log] tool finished: generate_practice_question
[log] model input messages: 3
[log] 2026-05-25 13:51:06 agent finished
[log] final message count: 4

TOOL:
Practice question for Python decorators: Write a decorator called `log_call` that prints the wrapped function's name before calling it. Apply it to a function called `add(a, b)` and show the expected output.

ASSISTANT:
Here's the solution:

**Code:**
```python
def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_call
def add(a, b):
    return a + b

# Example usage
add(3, 5)
```

**Expected Output:**
```
Calling add
8
```

The decorator prints "Calling add" before executing the function, then returns the result of the addition.


What Changed?
=============
This lab adds logging middleware:
- Logs agent start/finish timestamps
- Logs model input message count
- Logs tool start/finish events

Lab 26 will compose multiple middleware layers into a production agent.
