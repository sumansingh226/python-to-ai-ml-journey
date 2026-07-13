"""
Iterables and Iterators in Python

What is an Iterable?

An iterable is any object that can be looped over.

Examples:
- List
- Tuple
- String
- Dictionary
- Set
- File

An iterable contains multiple values
and can produce an iterator.

------------------------------------------------

What is an Iterator?

An iterator is an object that returns
one element at a time.

It remembers its current position.

Every iterator has two methods:

__iter__()
__next__()

------------------------------------------------

Why do we use Iterators?

1. Process one item at a time.
2. Save memory.
3. Work with large datasets.
4. Used internally by for loops.
5. Widely used in AI/ML.

------------------------------------------------

Difference

Iterable
---------
Collection of data.

Iterator
---------
Object that fetches data one by one.
"""


# ==========================================
# Example 1 : Iterable
# ==========================================

numbers = [10, 20, 30, 40]

for number in numbers:
    print(number)


"""
List is an iterable.

The for loop automatically creates
an iterator behind the scenes.
"""


print()


# ==========================================
# Example 2 : Creating Iterator
# ==========================================

numbers = [10, 20, 30]

iterator = iter(numbers)

print(iterator)


"""
iter()

Converts an iterable into an iterator.
"""


print()


# ==========================================
# Example 3 : next()
# ==========================================

numbers = [10, 20, 30]

iterator = iter(numbers)

print(next(iterator))

print(next(iterator))

print(next(iterator))


"""
Output

10
20
30
"""


print()


# ==========================================
# Example 4 : StopIteration
# ==========================================

numbers = [10, 20]

iterator = iter(numbers)

print(next(iterator))

print(next(iterator))

# print(next(iterator))

"""
Output

10
20

StopIteration

The iterator has no more elements.
"""


print()


# ==========================================
# Example 5 : Manual Iteration
# ==========================================

fruits = ["Apple", "Banana", "Mango"]

iterator = iter(fruits)

while True:

    try:
        item = next(iterator)
        print(item)

    except StopIteration:
        break


print()


# ==========================================
# Example 6 : String Iterator
# ==========================================

text = "Python"

iterator = iter(text)

print(next(iterator))
print(next(iterator))
print(next(iterator))


print()


# ==========================================
# Example 7 : Tuple Iterator
# ==========================================

numbers = (1, 2, 3)

iterator = iter(numbers)

for value in iterator:
    print(value)


print()


# ==========================================
# Example 8 : Dictionary Iterator
# ==========================================

student = {
    "name": "Suman",
    "age": 24
}

iterator = iter(student)

for key in iterator:
    print(key)


print()


# ==========================================
# Example 9 : Set Iterator
# ==========================================

skills = {"Python", "AI", "ML"}

iterator = iter(skills)

for skill in iterator:
    print(skill)


print()


# ==========================================
# Example 10 : File Iterator
# ==========================================

"""
with open("sample.txt", "r") as file:

    for line in file:
        print(line)

Files are iterators.

They return one line at a time.
"""


# ==========================================
# Example 11 : AI/ML Example
# ==========================================

dataset = [
    "Image 1",
    "Image 2",
    "Image 3"
]

iterator = iter(dataset)

print(next(iterator))
print(next(iterator))
print(next(iterator))


"""
Imagine these are images.

Instead of loading everything at once,
the iterator gives one image at a time.

This saves memory.
"""


print()


# ==========================================
# Example 12 : Checking Types
# ==========================================

numbers = [1, 2, 3]

iterator = iter(numbers)

print(type(numbers))

print(type(iterator))


"""
Output

<class 'list'>

<class 'list_iterator'>
"""


# ==========================================
# Example 13 : iter() Calls __iter__()
# ==========================================

numbers = [1, 2, 3]

iterator = numbers.__iter__()

print(next(iterator))
print(next(iterator))
print(next(iterator))


# ==========================================
# Example 14 : next() Calls __next__()
# ==========================================

numbers = [100, 200, 300]

iterator = iter(numbers)

print(iterator.__next__())
print(iterator.__next__())
print(iterator.__next__())


"""
Python internally does:

next(iterator)

↓

iterator.__next__()
"""
