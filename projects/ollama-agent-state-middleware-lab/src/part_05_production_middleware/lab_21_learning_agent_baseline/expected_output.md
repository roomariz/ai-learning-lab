21 Learning Agent Baseline (No Middleware)
==========================================

USER:
Explain what a Python decorator is

ASSISTANT:
A Python **decorator** is a special function that "wraps" another function to extend or modify its behavior **without changing the original code**. Think of it like a sticker you add to a function to give it extra powers (e.g., logging, timing, or access control).

### Example:
```python
def my_decorator(func):
    def wrapper():
        print("Before the function call!")
        func()  # Call the original function
        print("After the function call!")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
```

### Output:
```
Before the function call!
Hello!
After the function call!
```

### Key Points:
1. The `@my_decorator` syntax applies the decorator to `say_hello()`.
2. The decorator defines a `wrapper()` function that runs **before** and **after** the original function.
3. Decorators are useful for adding features like authentication, logging, or caching to functions cleanly.


USER:
Create a 7 day study plan for Python decorators

TOOL:
Created a 7-day study plan for Python decorators.

ASSISTANT:
Here's a 7-day study plan for Python decorators:

**Day 1: Foundations**
- Learn: What are decorators? How they modify functions
- Practice: Create a simple decorator (e.g., logging function calls)
- Question: Explain how `@decorator` syntax works

**Day 2: Patterns & Use Cases**
- Study: Decorator pattern principles
- Practice: Implement authentication decorator
- Question: How would you create a decorator that counts function calls?

**Day 3: Advanced Syntax**
- Learn: Decorators with arguments, nested decorators
- Practice: Build a timer decorator
- Question: Explain closures in decorators

**Day 4: Real-World Applications**
- Study: Decorators in frameworks (Flask/Django)
- Practice: Create a rate-limiting decorator
- Question: How do decorators affect function signatures?

**Day 5: Troubleshooting**
- Learn: Common decorator pitfalls
- Practice: Debug a decorator that breaks argument passing
- Question: Why would a decorator cause attribute errors?

**Day 6: Project Day**
- Build: Web app with authentication decorators
- Practice: Refactor code using decorators
- Question: How to create a decorator that caches results?

**Day 7: Mastery**
- Review: All concepts and patterns
- Practice: Design a custom decorator framework
- Final Project: Create a decorator for API request logging

Each day includes: 
1. Concept explanation
2. Code examples
3. Practice questions
4. Real-world application exercises

Would you like me to generate practice questions for specific days or topics?


USER:
Generate a practice question about Python decorators

TOOL:
Practice question for Python decorators: Write a decorator called `log_call` that prints the wrapped function's name before calling it. Apply it to a function called `add(a, b)` and show the expected output.

ASSISTANT:
Here's the practice question:

**Question:**  
Write a decorator called `log_call` that prints the wrapped function's name before calling it. Apply it to a function called `add(a, b)` and show the expected output when `add(3, 5)` is called.

**Example Output:**  
```
Calling add
8
```

---  
**Your Answer:**  
```python
# Student's code here
```

Would you like to submit your answer for grading?


No Middleware — What's Missing?
===============================
This baseline runs with zero production safeguards:
- All four tools are freely callable (no authz)
- No validation: empty, huge, or malicious input goes straight through
- No logging: zero observability into agent decisions
- No retries: a single tool failure kills the call
- No trimming: long message histories are not shortened before the model runs
- No error boundaries: unhandled exceptions crash the agent

Lab 22 will add tool authorisation middleware.