"""
Polymorphism in Python

What is Polymorphism?

The word Polymorphism comes from:

Poly = Many
Morph = Forms

Meaning:
One interface, many implementations.

In Python, different classes can have methods
with the same name but different behavior.

Why do we use Polymorphism?

1. Write flexible code
2. Reuse the same interface
3. Reduce complexity
4. Easily extend applications

Real-Life Example

Animal
↓

Dog  -> sound() -> Bark

Cat  -> sound() -> Meow

Cow  -> sound() -> Moo

Same method name:
sound()

Different behavior.
"""

# Basic Polymorphism example 

class Dog:

    def sound(self):
        print("Dog barks")


class Cat:

    def sound(self):
        print("Cat meows")


class Cow:

    def sound(self):
        print("Cow moos")


dog = Dog()
cat = Cat()
cow = Cow()

dog.sound()
cat.sound()
cow.sound()


print()
