"""
Methods in Python

What is a Method?

A method is a function defined inside a class.

Python has three types of methods:

1. Instance Method
2. Class Method
3. Static Method
"""


class Student:

    # Class Variable
    school = "ABC School"

    # Constructor
    def __init__(self, name, age):
        self.name = name
        self.age = age

    # Instance Method
    def display(self):
        print("Instance Method")
        print("Name :", self.name)
        print("Age  :", self.age)

    # Class Method
    @classmethod
    def show_school(cls):
        print("Class Method")
        print("School :", cls.school)

    # Static Method
    @staticmethod
    def welcome():
        print("Static Method")
        print("Welcome to Python OOP")


student = Student("Suman", 24)

student.display()

print()

Student.show_school()

print()

Student.welcome()