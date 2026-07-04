"""
Inheritance in Python

What is Inheritance?

Inheritance is a feature of Object-Oriented Programming
that allows one class (child class) to inherit the
properties and methods of another class (parent class).

Why do we use Inheritance?

1. Reuse existing code.
2. Reduce code duplication.
3. Make programs easier to maintain.
4. Build relationships between classes.

Real-Life Example

Parent
------
Animal

Child
-----
Dog
Cat
Bird

Every animal can:
- Eat
- Sleep

A dog also:
- Barks

A cat also:
- Meows


Types of Inheritance
1. Single Inheritance
2. Multilevel Inheritance
3. Multiple Inheritance
4. Hierarchical Inheritance
5. Hybrid Inheritance

Single Inheritance

Animal
   │
   ▼
 Dog
 
Multilevel Inheritance

LivingThing
      │
      ▼
   Animal
      │
      ▼
     Dog
Hierarchical Inheritance
        Animal
       /   |   \
     Dog  Cat  Bird
     
     

"""


#Example of inheritance 

class Model: 
    def train(self):
        print("Model is on training mode.")
    
    def predict(self):
        print("Making prediction")
        

class NaturalNetwork(Model):
    def backPropagation(self):
        print("Running backPropagation")

model = NaturalNetwork()

model.train()
model.predict()
model.backPropagation()

# Parent Class

class Animal:

    def eat(self):
        print("Animal is eating")

    def sleep(self):
        print("Animal is sleeping")


# Child Class

class Dog(Animal):

    def bark(self):
        print("Dog is barking")


dog = Dog()

dog.eat()
dog.sleep()
dog.bark()


print()