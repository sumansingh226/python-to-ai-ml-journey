"""
Constructors (__init__) in Python

What is a Constructor?

A constructor is a special method that is
automatically called whenever an object is created.

In Python, the constructor is written as:

__init__()

Why do we use Constructors?

1. Initialize object data
2. Assign values to object attributes
3. Avoid writing repetitive code
4. Automatically prepare the object

Real-Life Example

Imagine creating a Student.

Every student has:
- Name
- Age
- Course

Instead of setting these manually every time,
the constructor initializes them automatically.
"""


# Constructor Example

class Student:

    def __init__(self, name, age, course):
        self.name = name
        self.age = age
        self.course = course

    def display(self):
        print(f"Name   : {self.name}")
        print(f"Age    : {self.age}")
        print(f"Course : {self.course}")


# Creating Objects

student1 = Student("Suman", 24, "AI/ML")
student2 = Student("Rahul", 22, "Python")


# Calling Method

student1.display()

print()

student2.display()


# Another Example

class Car:

    def __init__(self, brand, model, price):
        self.brand = brand
        self.model = model
        self.price = price

    def details(self):
        print(f"Brand : {self.brand}")
        print(f"Model : {self.model}")
        print(f"Price : {self.price}")


car1 = Car("BMW", "X5", 8500000)

car1.details()

