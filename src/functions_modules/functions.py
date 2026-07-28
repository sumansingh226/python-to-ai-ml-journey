"""
Functions in Python

What is a Function?

A function is a reusable block of code that performs
a specific task.

Why do we use Functions?

1. Avoid code repetition
2. Improve code readability
3. Make code reusable
4. Break large programs into smaller parts
5. Easier testing and debugging

Real Life Example

Imagine a calculator.

Instead of writing addition logic every time,
we create one function and reuse it whenever needed.
"""

# Simple Function
def hello():
    print("hello from simple function")

hello()

# Function with Parameters

def printName(name):
    print(f"hello {name}")

printName("Suman singh")


# Function with Multiple Parameters

def add(a, b):
    print(a + b)

add(10, 20)


def multiply(a, b):
    return a * b

result = multiply(5, 10)

print(result)


def greet(name="Guest"):
    print(f"Hello {name}")

greet()
greet("Rahul")


# Keyword Arguments

def student(name, age):
    print(name, age)

student(age=25, name="Rahul")



# Arbitrary Arguments (*args)

# *args allows a function to accept any number of
# positional arguments.
# All passed values are stored inside a tuple.

def total(*nums):
    print(nums)
total(10, 20, 30, 40)

# Output:
# (10, 20, 30, 40)

# Explanation:
# numbers becomes a tuple containing all arguments.
# Useful when you don't know how many values
# the user will pass to the function.


# Arbitrary Keyword Arguments (**kwargs)

# **kwargs allows a function to accept any number of
# keyword arguments.
# All key-value pairs are stored inside a dictionary.

def profile(**data):
    print(data)

profile(name="Rahul", age=25 , income=5000)

# Output:
# {'name': 'Rahul', 'age': 25}

# Explanation:
# data becomes a dictionary.
# Keys are parameter names.
# Values are the values passed by the user.
# Useful when you don't know what information
# will be provided to the function.



# Scope Example

x = 100

def show():
    x = 10
    print("Inside:", x)

show()

print("Outside:", x)


# Function Calling Another Function

def greet():
    print("Hello")

def welcome():
    greet()
    print("Welcome")

welcome()