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