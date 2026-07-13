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

# Example 1 : Iterable

numbers = [10, 20, 30, 40]

for number in numbers:
    print(number)


"""
List is an iterable.

The for loop automatically creates
an iterator behind the scenes.
"""


print()
