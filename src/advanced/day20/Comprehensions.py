"""
List Comprehensions in Python

What is a List Comprehension?

A list comprehension is a short and
Pythonic way to create a new list.

It replaces long for loops with a
single readable line.

------------------------------------------------

Why do we use List Comprehensions?

1. Write shorter code.
2. Improve readability.
3. Faster than traditional loops.
4. Commonly used in AI/ML.
5. Create lists efficiently.

------------------------------------------------

Syntax

[expression for item in iterable]

With Condition

[expression for item in iterable if condition]
"""


# Example 1 : Without List Comprehension

numbers = [1, 2, 3, 4, 5]

squares = []

for number in numbers:
    squares.append(number ** 2)

print(squares)

print()


# Example 2 : With List Comprehension

numbers = [1, 2, 3, 4, 5]

squares = [number ** 2 for number in numbers]

print(squares)

print()

