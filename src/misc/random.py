"""
random Module in Python

The random module is used to generate
pseudo-random values.

------------------------------------------------

Common Functions

random.random()
random.randint()
random.randrange()
random.uniform()
random.choice()
random.choices()
random.sample()
random.shuffle()
random.seed()
"""

import random


# 1. Random Number Between 0 and 1

number = random.random()

print(number)

print()


# 2. Random Integer

number = random.randint(1, 10)

print(number)

print()


# 3. Random Number Using range

number = random.randrange(1, 20, 2)

print(number)

print()


# 4. Random Floating-Point Number

number = random.uniform(10, 20)

print(number)

print()


# 5. Random Choice

languages = [
    "Python",
    "Java",
    "C++",
    "JavaScript"
]

language = random.choice(languages)

print(language)

print()


# 6. Multiple Random Choices

languages = [
    "Python",
    "Java",
    "C++",
    "JavaScript"
]

selected = random.choices(
    languages,
    k=3
)

print(selected)

print()


# 7. Random Unique Items

numbers = [1, 2, 3, 4, 5, 6]

selected = random.sample(
    numbers,
    k=3
)

print(selected)

print()


# 8. Shuffle a List

numbers = [1, 2, 3, 4, 5]

random.shuffle(numbers)

print(numbers)

print()


# 9. Random Seed

random.seed(42)

print(random.randint(1, 100))

print(random.randint(1, 100))

print()


# 10. Simple Password Example

characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

password = ""

for i in range(6):

    password += random.choice(characters)

print(password)

print()

