"""
Lambda Functions in Python

What is a Lambda Function?

A lambda function is a small anonymous
function that can have any number of
arguments but only one expression.

Syntax

lambda arguments : expression

------------------------------------------------

Why do we use Lambda Functions?

1. Write short functions.
2. Avoid creating normal functions for simple tasks.
3. Used with map(), filter(), reduce().
4. Used for sorting.
5. Makes code concise.

------------------------------------------------

Difference

Normal Function
---------------
Uses def keyword.

Lambda Function
---------------
Uses lambda keyword.
"""



# Example 1 : Normal Function


def square(number):
    return number * number

print(square(5))

print()



# Example 2 : Lambda Function


square = lambda number: number * number

print(square(5))

print()



# Example 3 : Addition


add = lambda a, b: a + b

print(add(10, 20))

print()



# Example 4 : Multiplication


multiply = lambda a, b: a * b

print(multiply(5, 6))

print()



# Example 5 : Even or Odd


is_even = lambda number: number % 2 == 0

print(is_even(8))
print(is_even(9))

print()



# Example 6 : Maximum Number


maximum = lambda a, b: a if a > b else b

print(maximum(20, 15))

print()



# Example 7 : Sorting


students = [

    ("Rahul", 90),
    ("Amit", 80),
    ("Suman", 95)

]

students.sort(key=lambda student: student[1])

print(students)

print()



# Example 8 : String Length


words = [

    "Python",
    "AI",
    "Machine Learning"

]

words.sort(key=lambda word: len(word))

print(words)

print()



# Example 9 : AI/ML Example


models = [

    {"name": "CNN", "accuracy": 96},
    {"name": "SVM", "accuracy": 89},
    {"name": "Random Forest", "accuracy": 92}

]

models.sort(key=lambda model: model["accuracy"])

print(models)

print()



# Example 10 : Multiple Arguments


calculate = lambda a, b, c: a + b + c

print(calculate(10, 20, 30))