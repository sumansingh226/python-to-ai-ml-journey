"""
Tuples in Python

What is a Tuple?
A tuple is an ordered, immutable (cannot be changed)
collection of items.

Think of a tuple as a list whose contents should remain fixed.

Example:

coordinates = (10, 20)

Why Do We Use Tuples?

1. Store Multiple Values
------------------------
Tuples can hold multiple related values in a single variable.


Key Characteristics

✓ Ordered
✓ Immutable
✓ Allow duplicates
✓ Indexed
✓ Can store mixed data types

"""


#empty tuple
empty_tuple=()
#single item tuples 
single_tuple=(10,)
#multiple items
numbers=(1,5,6,10,7)
# Mixed data types
mixed = ("Rahul",25,False,5.9,2)
print(numbers)


# Accessing Elements

print(numbers[0])
print(numbers[1])
print(numbers[-1])

