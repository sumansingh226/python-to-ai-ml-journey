"""
Generators in Python

What is a Generator?

A generator is a special type of function
that returns one value at a time instead
of returning all values at once.

Generators use the 'yield' keyword.

------------------------------------------------

Why do we use Generators?

1. Save memory.
2. Process large datasets.
3. Produce values lazily (on demand).
4. Improve performance.
5. Used heavily in AI/ML and Data Science.

------------------------------------------------

Difference

Function
---------
Returns all at once.

Generator
----------
Returns one value at a time.
"""


# ==========================================
# Example 1 : Normal Function
# ==========================================

def numbers():

    return [1, 2, 3, 4, 5]


print(numbers())


print()


# ==========================================
# Example 2 : Generator Function
# ==========================================

def numbers():

    yield 1
    yield 2
    yield 3
    yield 4
    yield 5


generator = numbers()

print(generator)


print()


# ==========================================
# Example 3 : next()
# ==========================================

generator = numbers()

print(next(generator))
print(next(generator))
print(next(generator))
print(next(generator))
print(next(generator))


print()


# ==========================================
# Example 4 : Using for Loop
# ==========================================

generator = numbers()

for value in generator:
    print(value)


print()


# ==========================================
# Example 5 : Generator with Loop
# ==========================================

def count():

    for i in range(1, 6):
        yield i


generator = count()

for value in generator:
    print(value)


print()


# ==========================================
# Example 6 : Generator Expression
# ==========================================

squares = (x * x for x in range(1, 6))

for square in squares:
    print(square)


print()


# ==========================================
# Example 7 : StopIteration
# ==========================================

generator = numbers()

print(next(generator))
print(next(generator))
print(next(generator))
print(next(generator))
print(next(generator))

# print(next(generator))


"""
Calling next() again raises StopIteration.
"""


print()


# ==========================================
# Example 8 : Memory Efficient
# ==========================================

def huge_numbers():

    for i in range(1, 1000001):
        yield i


generator = huge_numbers()

print(next(generator))
print(next(generator))
print(next(generator))


"""
Only three numbers are generated.

The remaining values are created
only when needed.
"""


print()


# ==========================================
# Example 9 : Reading File Line by Line
# ==========================================

def read_file():

    with open("sample.txt", "r") as file:

        for line in file:
            yield line.strip()


"""
for line in read_file():
    print(line)
"""


print()


# ==========================================
# Example 10 : AI/ML Example
# ==========================================

def image_loader():

    images = [
        "Image 1",
        "Image 2",
        "Image 3"
    ]

    for image in images:
        yield image


for image in image_loader():
    print("Processing", image)


print()


# ==========================================
# Example 11 : Fibonacci Generator
# ==========================================

def fibonacci(limit):

    a = 0
    b = 1

    while a <= limit:

        yield a

        a, b = b, a + b


for number in fibonacci(50):
    print(number)


print()


# ==========================================
# Example 12 : Infinite Generator
# ==========================================

def infinite():

    number = 1

    while True:

        yield number

        number += 1


generator = infinite()

print(next(generator))
print(next(generator))
print(next(generator))
print(next(generator))
print(next(generator))


"""
The generator never ends.

It produces values only when requested.
"""