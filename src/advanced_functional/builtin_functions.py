"""
Built-in Functions

1. zip()
2. enumerate()
3. any()
4. all()

------------------------------------------------

What is zip()?

zip() combines two or more iterables
element by element.

------------------------------------------------

What is enumerate()?

enumerate() adds an index to each item
while iterating.

------------------------------------------------

What is any()?

Returns True if at least one element
is True.

------------------------------------------------

What is all()?

Returns True only if every element
is True.

------------------------------------------------

Why do we use them?

1. Write cleaner code.
2. Avoid manual indexing.
3. Combine multiple collections.
4. Validate conditions.
5. Used frequently in AI/ML.
"""
# Example 1 : zip()

names = ["Rahul", "Suman", "Amit"]
marks = [90, 95, 85]

result = zip(names, marks)

print(list(result))

"""
Output

[('Rahul', 90), ('Suman', 95), ('Amit', 85)]
"""

print()



# Example 2 : zip() with Loop

names = ["Rahul", "Suman", "Amit"]
ages = [22, 24, 21]

for name, age in zip(names, ages):
    print(name, age)

print()


# Example 3 : zip() Three Lists

names = ["Rahul", "Suman", "Amit"]
ages = [22, 24, 21]
cities = ["Delhi", "Mumbai", "Pune"]

for name, age, city in zip(names, ages, cities):
    print(name, age, city)

print()



# Example 5 : enumerate() Start Index
# ==========================================

languages = ["Python", "Java", "C++"]

for index, language in enumerate(languages, start=1):
    print(index, language)

print()


# Example 6 : any()

numbers = [False, False, True, False]

print(any(numbers))

"""
Output

True
"""

print()