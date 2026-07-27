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


# Example 3 : Even Numbers

numbers = range(1, 11)

even_numbers = [number for number in numbers if number % 2 == 0]

print(even_numbers)

print()


# Example 4 : Odd Numbers

numbers = range(1, 11)

odd_numbers = [number for number in numbers if number % 2 != 0]

print(odd_numbers)

print()


# Example 5 : Convert to Uppercase

languages = ["python", "java", "c++"]

uppercase = [language.upper() for language in languages]

print(uppercase)

print()


# Example 6 : String Length

words = ["Python", "AI", "Machine Learning"]

lengths = [len(word) for word in words]

print(lengths)

print()


# Example 7 : Multiplication Table

table = [number * 5 for number in range(1, 11)]

print(table)

print()


# Example 8 : Replace Negative Numbers

numbers = [-5, 10, -8, 20, 15]

positive = [0 if number < 0 else number for number in numbers]

print(positive)

print()


# Example 9 : Nested List Comprehension

matrix = [

    [1, 2, 3],

    [4, 5, 6],

    [7, 8, 9]

]

flatten = [number for row in matrix for number in row]

print(flatten)

print()


# Example 10 : AI/ML Example

accuracies = [91, 95, 88, 97, 93]

improved = [accuracy + 1 for accuracy in accuracies]

print(improved)

print()


# Example 11 : Filter High Accuracy

accuracies = [91, 95, 88, 97, 93]

high_accuracy = [accuracy for accuracy in accuracies if accuracy >= 95]

print(high_accuracy)

print()


# Example 12 : Square Only Even Numbers

numbers = range(1, 11)

result = [number ** 2 for number in numbers if number % 2 == 0]

print(result)