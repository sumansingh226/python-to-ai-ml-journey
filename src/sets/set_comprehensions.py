"""
Set Comprehensions in Python

What is a Set Comprehension?

A set comprehension is a short and
Pythonic way to create sets.

It allows us to generate unique values
using a single line of code.

------------------------------------------------

Why do we use Set Comprehensions?

1. Create sets quickly.
2. Remove duplicate values.
3. Write shorter code.
4. Improve readability.
5. Useful in Data Science and AI/ML.

------------------------------------------------

Syntax

{expression for item in iterable}

With Condition

{expression for item in iterable if condition}
"""

# Example 1 : Normal Way

numbers = [1, 2, 3, 4, 5]

squares = set()

for number in numbers:
    squares.add(number ** 2)

print(squares)


print()


# Example 2 : Set Comprehension
# ==========================================

numbers = [1, 2, 3, 4, 5]

squares = {number ** 2 for number in numbers}

print(squares)


print()


# Example 3 : Remove Duplicates

numbers = [1, 2, 2, 3, 3, 4, 5, 5]

unique_numbers = {number for number in numbers}

print(unique_numbers)


print()