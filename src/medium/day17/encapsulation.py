"""
Encapsulation in Python

What is Encapsulation?

Encapsulation is the process of combining data (variables)
and methods (functions) into a single class while controlling
direct access to the data.

In simple words:

Encapsulation means protecting an object's data
from being accessed or modified directly.

Why do we use Encapsulation?

1. Protect sensitive data.
2. Prevent accidental changes.
3. Improve security.
4. Keep code organized.
5. Control how data is accessed and updated.

Real-Life Example

Think of an ATM.

You can:
✓ Deposit money
✓ Withdraw money
✓ Check balance

But you cannot directly change your bank balance
by typing:

balance = 1000000

The ATM controls access to the balance.

This is Encapsulation.
"""


# Example 1 : Public Variable

class Student:

    def __init__(self, name):
        self.name = name


student = Student("Suman")

print(student.name)

student.name = "Rahul"

print(student.name)




print()