"""
Generators in Python

What is a Generator?

A generator is a special type of function
that returns one value at a time instead
of returning all values at once.

Generators use the keyword:

yield

instead of:

return

--------------------------------------------

Why do we use Generators?

1. Save memory.
2. Process large data.
3. Produce values one by one.
4. Create iterators easily.
5. Used heavily in AI/ML.

--------------------------------------------

return vs yield

return
-------
Returns one value.
Function ends.

yield
------
Returns one value.
Function pauses.
Continues from where it stopped.
"""


# ==========================================
# Example 1 : Normal Function
# ==========================================

def numbers():

    return [1, 2, 3]


print(numbers())

print()


# ==========================================
# Example 2 : Generator Function
# ==========================================

def numbers():

    yield 1
    yield 2
    yield 3


generator = numbers()

print(generator)

print()


# ==========================================
# Example 3 : next()
# ==========================================

def numbers():

    yield 10
    yield 20
    yield 30


generator = numbers()

print(next(generator))
print(next(generator))
print(next(generator))

print()


# ==========================================
# Example 4 : for Loop
# ==========================================

def colors():

    yield "Red"
    yield "Green"
    yield "Blue"


for color in colors():

    print(color)

print()


# ==========================================
# Example 5 : Generator Pauses
# ==========================================

def demo():

    print("Step 1")
    yield 100

    print("Step 2")
    yield 200

    print("Step 3")
    yield 300


generator = demo()

print(next(generator))
print(next(generator))
print(next(generator))

print()


# ==========================================
# Example 6 : Generator Expression
# ==========================================

numbers = (x * x for x in range(5))

for number in numbers:

    print(number)

print()


# ==========================================
# Example 7 : Large Dataset
# ==========================================

def dataset():

    for i in range(1, 6):

        yield f"Image {i}"


for image in dataset():

    print(image)

print()


# ==========================================
# Example 8 : Infinite Generator
# ==========================================

def counter():

    number = 1

    while True:

        yield number

        number += 1


generator = counter()

print(next(generator))
print(next(generator))
print(next(generator))
print(next(generator))
print(next(generator))

print()


# ==========================================
# Example 9 : Reading File
# ==========================================

"""
with open("sample.txt") as file:

    for line in file:

        print(line)

Files internally work like generators.
"""

print()


# ==========================================
# Example 10 : AI/ML Example
# ==========================================

def data_loader():

    images = [
        "cat.jpg",
        "dog.jpg",
        "bird.jpg"
    ]

    for image in images:

        yield image


for image in data_loader():

    print("Processing:", image)