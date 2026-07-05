"""What is Abstraction?

Abstraction is an Object-Oriented Programming (OOP) concept that hides the implementation details and shows only the essential features to the user.

For example, when you drive a car, you use the steering wheel, accelerator, and brakes without needing to know how the engine works internally.

Abstraction in Python

Python provides abstraction using the abc (Abstract Base Class) module."""

#example : 
from abc import ABC, abstractmethod

# Abstract class
class Animal(ABC):

    @abstractmethod
    def sound(self):
        pass

# Child class
class Dog(Animal):
    def sound(self):
        return "Bark"

# Child class
class Cat(Animal):
    def sound(self):
        return "Meow"

dog = Dog()
cat = Cat()

print(dog.sound())  # Bark
print(cat.sound())  # Meow