"""
super() in Python

What is super()?

super() is a built-in function that allows a child class
to access the methods and constructor of its parent class.

Why do we use super()?

1. Reuse parent class code.
2. Avoid duplicate code.
3. Call the parent constructor.
4. Extend parent functionality.

Real-Life Example

Parent
------
Person

Child
-----
Student

Every student is also a person.

Instead of writing Person's code again,
we reuse it using super().
"""

# Calling Parent Method

class Animal:

    def eat(self):
        print("Animal is eating")


class Dog(Animal):

    def bark(self):
        print("Dog is barking")

    def show(self):

        # Call Parent Method
        super().eat()

        print("Inside Child Class")


dog = Dog()

dog.show()
