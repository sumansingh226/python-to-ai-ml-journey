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



# Example 2 : With Dictionary Comprehension


numbers = [1, 2, 3, 4, 5]

squares = {number: number ** 2 for number in numbers}

print(squares)

print()



# Example 3 : Even Numbers


numbers = range(1, 11)

even_squares = {
    number: number ** 2
    for number in numbers
    if number % 2 == 0
}

print(even_squares)

print()



# Example 4 : Word Length


words = ["Python", "AI", "Machine Learning"]

lengths = {word: len(word) for word in words}

print(lengths)

print()



# Example 5 : Celsius to Fahrenheit


celsius = [0, 10, 20, 30]

fahrenheit = {
    temp: (temp * 9 / 5) + 32
    for temp in celsius
}

print(fahrenheit)

print()



# Example 6 : Uppercase Values


languages = ["python", "java", "c++"]

result = {
    language: language.upper()
    for language in languages
}

print(result)

print()



# Example 7 : Dictionary Transformation


marks = {

    "Rahul": 80,
    "Suman": 95,
    "Amit": 70

}

updated = {
    name: mark + 5
    for name, mark in marks.items()
}

print(updated)

print()



# Example 8 : Pass Students


marks = {

    "Rahul": 80,
    "Suman": 95,
    "Amit": 35,
    "Priya": 60

}

passed = {
    name: mark
    for name, mark in marks.items()
    if mark >= 40
}

print(passed)

print()



# Example 9 : AI/ML Example


models = {

    "CNN": 95,
    "SVM": 89,
    "Random Forest": 92

}

improved = {
    model: accuracy + 1
    for model, accuracy in models.items()
}

print(improved)

print()



# Example 10 : Label Encoding

labels = [

    "Cat",
    "Dog",
    "Bird"

]

encoding = {
    label: index
    for index, label in enumerate(labels)
}

print(encoding)