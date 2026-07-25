"""
List Comprehensions in Python

What is a List Comprehension?

A list comprehension is a short and elegant
way to create a new list using a single line
of code.

It replaces many traditional for loops.

------------------------------------------------

Why do we use List Comprehensions?

1. Write less code.
2. Improve readability.
3. Faster than manual loops.
4. Transform data easily.
5. Used heavily in AI/ML.

------------------------------------------------

Syntax

[expression for item in iterable]

With Condition

[expression for item in iterable if condition]
"""


# ==========================================
# Example 1 : Traditional Method
# ==========================================

numbers = [1, 2, 3, 4, 5]

squares = []

for number in numbers:
    squares.append(number * number)

print(squares)

print()


# ==========================================
# Example 2 : List Comprehension
# ==========================================

numbers = [1, 2, 3, 4, 5]

squares = [number * number for number in numbers]

print(squares)

print()


# ==========================================
# Example 3 : Even Numbers
# ==========================================

numbers = range(1, 11)

even = [number for number in numbers if number % 2 == 0]

print(even)

print()


# ==========================================
# Example 4 : Odd Numbers
# ==========================================

numbers = range(1, 11)

odd = [number for number in numbers if number % 2 != 0]

print(odd)

print()


# ==========================================
# Example 5 : Uppercase Strings
# ==========================================

languages = ["python", "java", "c++"]

upper = [language.upper() for language in languages]

print(upper)

print()


# ==========================================
# Example 6 : String Length
# ==========================================

words = ["AI", "Python", "Machine Learning"]

lengths = [len(word) for word in words]

print(lengths)

print()


# ==========================================
# Example 7 : Squares
# ==========================================

numbers = range(1, 11)

result = [number ** 2 for number in numbers]

print(result)

print()


# ==========================================
# Example 8 : Cubes
# ==========================================

numbers = range(1, 6)

result = [number ** 3 for number in numbers]

print(result)

print()


# ==========================================
# Example 9 : If-Else
# ==========================================

numbers = range(1, 11)

result = ["Even" if number % 2 == 0 else "Odd" for number in numbers]

print(result)

print()


# ==========================================
# Example 10 : First Letter
# ==========================================

names = ["Rahul", "Suman", "Amit"]

letters = [name[0] for name in names]

print(letters)

print()


# ==========================================
# Example 11 : Flatten Nested List
# ==========================================

matrix = [

    [1, 2],
    [3, 4],
    [5, 6]

]

flat = [number for row in matrix for number in row]

print(flat)

print()


# ==========================================
# Example 12 : AI/ML Example
# ==========================================

predictions = [0.2, 0.8, 0.45, 0.9]

binary = [1 if value >= 0.5 else 0 for value in predictions]

print(binary)

print()


# ==========================================
# Example 13 : Normalize Data
# ==========================================

scores = [50, 60, 70, 80, 90]

normalized = [score / 100 for score in scores]

print(normalized)

print()


# ==========================================
# Example 14 : Remove Empty Strings
# ==========================================

data = ["Python", "", "AI", "", "ML"]

clean = [item for item in data if item != ""]

print(clean)