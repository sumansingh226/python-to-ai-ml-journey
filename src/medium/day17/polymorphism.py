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



#One Function, Many Objects
class Dog:

    def speak(self):
        print("Dog barks")


class Cat:

    def speak(self):
        print("Cat meows")


class Bird:

    def speak(self):
        print("Bird chirps")


def make_sound(animal):
    animal.speak()


make_sound(Dog())
make_sound(Cat())
make_sound(Bird())


print()


 #Inheritance + Polymorphism

class Animal:

    def sound(self):
        print("Animal makes a sound")


class Dog(Animal):

    def sound(self):
        print("Dog barks")


class Cat(Animal):

    def sound(self):
        print("Cat meows")


animals = [Dog(), Cat()]

for animal in animals:
    animal.sound()


print()

#AI/ML Example

class Model:

    def train(self):
        print("Training generic model")


class DecisionTree(Model):

    def train(self):
        print("Training Decision Tree")


class RandomForest(Model):

    def train(self):
        print("Training Random Forest")


class NeuralNetwork(Model):

    def train(self):
        print("Training Neural Network")


models = [
    DecisionTree(),
    RandomForest(),
    NeuralNetwork()
]

for model in models:
    model.train()