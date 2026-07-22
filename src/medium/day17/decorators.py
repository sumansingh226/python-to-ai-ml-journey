"""
Decorators in Python

What is a Decorator?

A decorator is a function that takes another
function as input, adds some extra functionality,
and returns a new function.

In simple words:

Decorator = Wrap a function with extra behavior.

------------------------------------------------

Why do we use Decorators?

1. Avoid duplicate code.
2. Add logging.
3. Add authentication.
4. Measure execution time.
5. Validate input.
6. Used in Flask, Django, FastAPI, AI/ML libraries.

------------------------------------------------

Real-Life Example

Think of a gift.

Gift
↓

Decorator (Gift Wrapper)

↓

Wrapped Gift

The gift stays the same.
Only extra wrapping is added.

Similarly,

Original Function
↓

Decorator

↓

Enhanced Function
"""

# ==========================================
# Example 1 : Function is an Object
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


# ==========================================
# Example 3 : Returning Function
# ==========================================

def outer():

    def inner():
        print("Hello from Inner Function")

    return inner

message = outer()

message()

print()


# ==========================================
# Example 4 : Basic Decorator
# ==========================================

def decorator(function):

    def wrapper():

        print("Before Function")

        function()

        print("After Function")

    return wrapper


def greet():
    print("Welcome to Python")


greet = decorator(greet)

greet()

print()


# ==========================================
# Example 5 : @ Decorator Syntax
# ==========================================

def decorator(function):

    def wrapper():

        print("Before Function")

        function()

        print("After Function")

    return wrapper


@decorator
def hello():
    print("Hello World")


hello()

print()


# ==========================================
# Example 6 : Decorator with Arguments
# ==========================================

def decorator(function):

    def wrapper(name):

        print("Before Function")

        function(name)

        print("After Function")

    return wrapper


@decorator
def greet(name):

    print("Hello", name)


greet("Suman")

print()


# ==========================================
# Example 7 : Execution Time
# ==========================================

import time

def timer(function):

    def wrapper():

        start = time.time()

        function()

        end = time.time()

        print("Execution Time:", end - start)

    return wrapper


@timer
def task():

    time.sleep(2)

    print("Task Completed")


task()

print()


# ==========================================
# Example 8 : Authentication Example
# ==========================================

def login_required(function):

    def wrapper():

        logged_in = True

        if logged_in:
            function()
        else:
            print("Please Login")

    return wrapper


@login_required
def dashboard():

    print("Welcome to Dashboard")


dashboard()

print()


# ==========================================
# Example 9 : AI/ML Example
# ==========================================

def logger(function):

    def wrapper():

        print("Training Started")

        function()

        print("Training Finished")

    return wrapper


@logger
def train_model():

    print("Training Neural Network...")


train_model()