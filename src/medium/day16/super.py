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
