"""
Lambda Functions in Python

What is a Lambda Function?

A lambda function is a small anonymous
(unnamed) function.

It can take any number of arguments
but contains only one expression.

Syntax

lambda arguments : expression

------------------------------------------------

Why do we use Lambda Functions?

1. Write short functions.
2. Avoid creating functions used only once.
3. Work with map(), filter(), reduce().
4. Used in sorting.
5. Common in Data Science and AI/ML.

------------------------------------------------

Difference

Normal Function
---------------
Uses def

Lambda Function
---------------
Uses lambda
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

print(is_even(10))
print(is_even(7))


print()


# Example 6 : Maximum Number

maximum = lambda a, b: a if a > b else b

print(maximum(15, 25))


print()


# Example 7 : String Length

length = lambda text: len(text)

print(length("Python"))


print()


# Example 8 : Sorting

students = [

    ("Rahul", 80),
    ("Suman", 95),
    ("Amit", 70)

]

students.sort(key=lambda student: student[1])

print(students)


print()


# Example 9 : AI/ML Example

predictions = [0.45, 0.90, 0.25, 0.80]

predictions.sort(key=lambda value: value)

print(predictions)


print()


# Example 10 : Multiple Arguments

information = lambda name, age: f"{name} is {age} years old"

print(information("Suman", 24))