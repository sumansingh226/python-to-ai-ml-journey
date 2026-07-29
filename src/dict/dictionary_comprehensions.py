"""
Dictionary Comprehensions in Python

What is a Dictionary Comprehension?

A dictionary comprehension is a short
and Pythonic way to create dictionaries.

It allows us to generate key-value pairs
using a single line of code.

------------------------------------------------

Why do we use Dictionary Comprehensions?

1. Write shorter code.
2. Improve readability.
3. Create dictionaries quickly.
4. Transform existing dictionaries.
5. Common in Data Science and AI/ML.

------------------------------------------------

Syntax

{key : value for item in iterable}

With Condition

{key : value for item in iterable if condition}
"""

# Example 1 : Without Dictionary Comprehension

numbers = [1, 2, 3, 4, 5]

squares = {}

for number in numbers:
    squares[number] = number ** 2

print(squares)

print()

