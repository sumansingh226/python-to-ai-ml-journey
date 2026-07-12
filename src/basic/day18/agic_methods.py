"""
Magic (Dunder) Methods in Python

What are Magic Methods?

Magic methods are special methods in Python that
begin and end with double underscores (__).

They allow Python objects to work with built-in
operations like printing, adding, comparing, and more.

"Dunder" stands for "Double UNDERscore."

Examples:

__init__()
__str__()
__repr__()
__len__()
__add__()
__eq__()

Why do we use Magic Methods?

1. Customize object behavior.
2. Work with Python built-in functions.
3. Make objects behave like built-in types.
4. Improve readability.
"""


# Example 1 : __init__

class Student:

    def __init__(self, name):
        self.name = name


student = Student("Suman")

print(student.name)


print()