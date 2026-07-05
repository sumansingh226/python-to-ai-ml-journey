""" Polymorphism in Python is an Object-Oriented Programming (OOP) concept where the same method or function can behave differently depending on the object that calls it. This allows you to write flexible and reusable code.""

example 

class Animal:
    def sound(self):
        print("Animal makes a sound")

class Dog(Animal):
    def sound(self):
        print("Dog barks")

class Cat(Animal):
    def sound(self):
        print("Cat meows")

# Creating objects
dog = Dog()
cat = Cat()

# Polymorphism
dog.sound()   # Output: Dog barks
cat.sound()   # Output: Cat meows


#Polymorphism Using a Common Function
class Dog:
    def sound(self):
        return "Bark"

class Cat:
    def sound(self):
        return "Meow"

class Cow:
    def sound(self):
        return "Moo"

def animal_sound(animal):
    print(animal.sound())

# Objects
dog = Dog()
cat = Cat()
cow = Cow()

# Same function works with different objects
animal_sound(dog)
animal_sound(cat)
animal_sound(cow)



