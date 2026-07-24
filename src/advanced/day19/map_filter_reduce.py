"""
map(), filter(), reduce() in Python

What is map()?

map() applies a function to every item
in an iterable and returns a map object.

Syntax

map(function, iterable)

------------------------------------------------

What is filter()?

filter() selects only those elements
that satisfy a condition.

Syntax

filter(function, iterable)

------------------------------------------------

What is reduce()?

reduce() repeatedly applies a function
to reduce multiple values into a single value.

Syntax

from functools import reduce

reduce(function, iterable)

------------------------------------------------

Why do we use them?

1. Process collections efficiently.
2. Write cleaner code.
3. Avoid manual loops.
4. Used in Data Science.
5. Used in AI/ML preprocessing.
"""

from functools import reduce



# Example 1 : map()


numbers = [1, 2, 3, 4, 5]

squares = map(lambda x: x * x, numbers)

print(list(squares))

print()



# Example 2 : map() with Function


def cube(number):
    return number ** 3

numbers = [1, 2, 3, 4]

result = map(cube, numbers)

print(list(result))

print()



# Example 3 : Convert to Uppercase


names = ["python", "java", "c++"]

result = map(str.upper, names)

print(list(result))

print()



# Example 4 : filter()


numbers = [1,2,3,4,5,6,7,8,9,10]

even = filter(lambda x: x % 2 == 0, numbers)

print(list(even))

print()



# Example 5 : Filter Strings


names = ["AI", "Python", "ML", "Deep Learning"]

result = filter(lambda x: len(x) > 2, names)

print(list(result))

print()



# Example 6 : reduce()


numbers = [1,2,3,4,5]

sum_numbers = reduce(lambda x, y: x + y, numbers)

print(sum_numbers)

print()



# Example 7 : Find Maximum


numbers = [15, 8, 42, 19, 30]

maximum = reduce(lambda x, y: x if x > y else y, numbers)

print(maximum)

print()



# Example 8 : Product


numbers = [1,2,3,4]

product = reduce(lambda x, y: x * y, numbers)

print(product)

print()



# Example 9 : AI/ML Example


predictions = [0.2, 0.8, 0.6, 0.1]

binary = list(map(lambda x: 1 if x >= 0.5 else 0, predictions))

print(binary)

print()



# Example 10 : AI/ML Data Cleaning


scores = [45, 80, 35, 90, 70]

passed = list(filter(lambda x: x >= 50, scores))

print(passed)

print()



# Example 11 : Total Accuracy


accuracies = [91, 94, 97]

average = reduce(lambda x, y: x + y, accuracies) / len(accuracies)

print(average)