
30 Cost Tracking Middleware
===========================
Goal: visibility into rough local cost signals.
Logs: request started, message count, tool call count, estimated cost.


USER:
Explain Python decorators using explain_topic, then create a 3-day study plan using create_study_plan.
[cost] request started
[cost] messages: 1
[cost] messages: 4
[cost] tool calls: 2
[cost] elapsed_ms: 67643
[cost] estimated_local_compute_load: medium

ASSISTANT:
### Python Decorators Explained Simply:
A **decorator** is a tool in Python that lets you modify or enhance a function’s behavior without changing its code. Think of it like a "wrapper" that adds extra functionality.  

**Example**:  
```python
def greet(name):
    return f"Hello, {name}!"

@greet  # This is a decorator
def say_hi():
    return "Hi!"

print(say_hi())  # Output: Hello, Hi!
```  
Here, `@greet` wraps the `say_hi` function, adding the "Hello, " prefix. Decorators are commonly used for tasks like **logging**, **timing**, or **access control**.

---

### 3-Day Python Study Plan:
**Day 1**: Basics  
- Learn syntax, variables, data types (lists, dicts), and basic I/O.  
- Practice: Write a program to calculate your age from user input.  

**Day 2**: Functions & Control Flow  
- Master functions, loops (`for`, `while`), and conditionals (`if-else`).  
- Practice: Build a simple calculator with error handling.  

**Day 3**: Advanced Concepts  
- Study decorators, modules, and file handling.  
- Practice: Create a decorator that logs function execution time.  

Let me know if you’d like adjustments! 😊