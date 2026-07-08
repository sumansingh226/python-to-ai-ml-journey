"""
Method Overriding in Python

What is Method Overriding?

Method overriding occurs when a child class
provides its own implementation of a method
that already exists in the parent class.

The child method replaces the parent method.

Why do we use Method Overriding?

1. Customize inherited behavior.
2. Extend parent functionality.
3. Implement specific behavior for child classes.

Real-Life Example

Parent
------
Animal -> sound()

Child
-----
Dog -> sound()

Every animal makes a sound,
but each animal has its own sound.
"""

#basic example 
class Animal:

    def sound(self):
        print("Animals make sounds")


class Dog(Animal):

    def sound(self):
        print("Dog barks")


dog = Dog()

dog.sound()


# Parent Method Not Overridden

class Animal:

    def eat(self):
        print("Animal is eating")


class Dog(Animal):
    pass


dog = Dog()

dog.eat()

