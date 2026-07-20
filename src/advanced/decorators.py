"""
Decorators in Python

What is a Decorator?

A decorator is a function that takes another function,
adds extra functionality to it, and returns the modified function.

A decorator allows us to change the behavior of a function
without changing its original code.

------------------------------------------------

Why do we use Decorators?

1. Reuse code.
2. Avoid duplicate code.
3. Add logging.
4. Check permissions.
5. Measure execution time.
6. Authentication & Authorization.
7. Used in Flask, Django, FastAPI, and AI/ML libraries.

------------------------------------------------

Real-Life Example

Imagine a gift.

Original Gift
↓

Decorator (Gift Wrapper)

↓

Beautiful Wrapped Gift

The gift is the same,
only extra functionality is added.

Similarly,

Original Function
↓

Decorator

↓

Enhanced Function
"""

# Example 1 : Function as an Object
# ==========================================

def greet():
    print("Hello")

message = greet

message()

print()


# ==========================================
# Example 2 : Function Inside Function
# ==========================================

def outer():

    def inner():
        print("Inside Inner Function")

    inner()

outer()

print()