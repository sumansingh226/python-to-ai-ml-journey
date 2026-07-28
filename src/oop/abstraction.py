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



# Key Points
# ABC is used to create an abstract class.
# @abstractmethod declares a method that must be implemented by child classes.
# You cannot create an object of an abstract class.

# For example, this will raise an error:

animal = Animal()   # Error


# Benefits of Abstraction
# Hides unnecessary implementation details.
# Makes code easier to understand.
# Improves code reusability.
# Enforces a common interface for subclasses.