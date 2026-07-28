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




# Example 2 : Protected Variable

class Employee:

    def __init__(self, salary):
        self._salary = salary


employee = Employee(50000)

print(employee._salary)

employee._salary = 70000

print(employee._salary)




print()





# Example 3 : Private Variable

class BankAccount:

    def __init__(self, balance):
        self.__balance = balance

    def show_balance(self):
        print("Balance:", self.__balance)


account = BankAccount(10000)

account.show_balance()



print()



# Example 4 : Getter Method

class Person:

    def __init__(self, age):
        self.__age = age

    def get_age(self):
        return self.__age


person = Person(24)

print(person.get_age())


print()


# Example 5 : Setter Method

class Person:

    def __init__(self):
        self.__age = 0

    def set_age(self, age):

        if age >= 0:
            self.__age = age
        else:
            print("Invalid age")

    def get_age(self):
        return self.__age


person = Person()

person.set_age(24)

print(person.get_age())

person.set_age(-10)


print()
