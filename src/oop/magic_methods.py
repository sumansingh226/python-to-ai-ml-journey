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

"""
Magic Method	Purpose
__init__	Initialize an object
__str__	String representation for print()
__repr__	Official object representation
__len__	Called by len()
__add__	Called by +
__sub__	Called by -
__mul__	Called by *
__truediv__	Called by /
__eq__	Called by ==
__lt__	Called by <
__gt__	Called by >

Why Are Magic Methods Important?

Python's built-in types (list, dict, str, int) all use magic methods behind the scenes.
By implementing them in your own classes, you can make your objects behave naturally with Python's syntax and built-in functions.


"""

# Example 1 : __init__

class Student:

    def __init__(self, name):
        self.name = name


student = Student("Suman")

print(student.name)


print()


# Example 2 : __str__

class Student:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Student(Name={self.name})"


student = Student("Suman")

print(student)


print()


# Example 3 : __len__

class Book:

    def __init__(self, pages):
        self.pages = pages

    def __len__(self):
        return self.pages


book = Book(350)

print(len(book))


print()


# Example 4 : __add__

class Number:

    def __init__(self, value):
        self.value = value

    def __add__(self, other):
        return self.value + other.value


num1 = Number(10)
num2 = Number(20)

print(num1 + num2)


print()


# Example 5 : __eq__

class Student:

    def __init__(self, age):
        self.age = age

    def __eq__(self, other):
        return self.age == other.age


s1 = Student(24)
s2 = Student(24)

print(s1 == s2)


print()


# Example 6 : AI/ML Example

class Tensor:

    def __init__(self, value):
        self.value = value

    def __add__(self, other):
        return Tensor(self.value + other.value)

    def __str__(self):
        return f"Tensor({self.value})"


t1 = Tensor(5)
t2 = Tensor(10)

print(t1 + t2)