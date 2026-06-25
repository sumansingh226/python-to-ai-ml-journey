"""
PACKAGES IN PYTHON

What is a Package?

A package is a folder that contains one or more Python modules.

Module  = Python file (.py)
Package = Folder containing Python files

Why do we use Packages?

1. Organize code
2. Group related modules together
3. Avoid huge files
4. Improve project structure
5. Make code reusable

Real Life Example

Imagine an AI project:

ai_project/

├── data/
├── models/
├── utils/
├── training/
└── main.py

Instead of putting 5000 lines in one file,
we split code into packages and modules.
"""



"""
Packages and Modules (Single File Demonstration)

In a real project:

calculator.py  -> Module
helper.py      -> Module

utils/         -> Package

For learning purposes, we will keep everything
inside one file.
"""


# =========================
# calculator.py (Module)
# =========================

def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


# =========================
# helper.py (Module)
# =========================

def greet(name):
    print(f"Hello {name}")


def goodbye(name):
    print(f"Goodbye {name}")


# =========================
# main.py
# =========================

print("Using Calculator Module")

result1 = add(10, 20)
result2 = multiply(5, 6)

print("Addition:", result1)
print("Multiplication:", result2)

print()

print("Using Helper Module")

greet("Rahul")
goodbye("Rahul")