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


numbers = [1, 2, 3, 4, 5]

squares = {number ** 2 for number in numbers}

print(squares)


print()



# Example 3 : Remove Duplicates


numbers = [1, 2, 2, 3, 3, 4, 5, 5]

unique_numbers = {number for number in numbers}

print(unique_numbers)


print()



# Example 4 : Even Numbers


numbers = range(1, 11)

even_numbers = {
    number
    for number in numbers
    if number % 2 == 0
}

print(even_numbers)


print()



# Example 5 : Odd Numbers


numbers = range(1, 11)

odd_numbers = {
    number
    for number in numbers
    if number % 2 != 0
}

print(odd_numbers)


print()



# Example 6 : Convert Strings


languages = [
    "python",
    "java",
    "python",
    "c++"
]


upper_languages = {
    language.upper()
    for language in languages
}


print(upper_languages)


print()



# Example 7 : Length of Words


words = [
    "Python",
    "AI",
    "Machine Learning"
]


lengths = {
    len(word)
    for word in words
}


print(lengths)


print()



# Example 8 : Filter Values


marks = [
    45,
    80,
    90,
    30,
    95
]


passed_marks = {
    mark
    for mark in marks
    if mark >= 50
}


print(passed_marks)


print()



# Example 9 : AI/ML Example


predictions = [
    "Cat",
    "Dog",
    "Cat",
    "Bird",
    "Dog"
]


classes = {
    prediction
    for prediction in predictions
}


print(classes)


print()



# Example 10 : Extract Unique Features


dataset = [

    ["age", "salary"],

    ["age", "city"],

    ["salary", "experience"]

]


features = {
    feature
    for row in dataset
    for feature in row
}


print(features)