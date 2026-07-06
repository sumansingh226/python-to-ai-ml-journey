"""
Polymorphism in Python

Polymorphism is an Object-Oriented Programming (OOP) concept where
the same method or function behaves differently depending on the
object that calls it. It allows you to write flexible and reusable code.
"""

print("=" * 50)
print("1. Polymorphism Using Method Overriding")
print("=" * 50)


# Parent class
class Animal:
    def sound(self):
        print("Animal makes a sound")


# Child classes
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
dog.sound()
cat.sound()


print("\n" + "=" * 50)
print("2. Polymorphism Using a Common Function (Duck Typing)")
print("=" * 50)


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


# Creating objects
dog = Dog()
cat = Cat()
cow = Cow()

# Same function works with different objects
animal_sound(dog)
animal_sound(cat)
animal_sound(cow)


print("\n" + "=" * 50)
print("3. Built-in Polymorphism")
print("=" * 50)

print(len("Python"))             # 6
print(len([10, 20, 30, 40]))     # 4
print(len((1, 2, 3)))            # 3


print("\n" + "=" * 50)
print("4. Polymorphism with Method Overriding")
print("=" * 50)


class Bird:
    def fly(self):
        print("Bird can fly")


class Sparrow(Bird):
    def fly(self):
        print("Sparrow flies high")


class Penguin(Bird):
    def fly(self):
        print("Penguin cannot fly")


birds = [Sparrow(), Penguin()]

for bird in birds:
    bird.fly()


print("\n" + "=" * 50)
print("Advantages of Polymorphism")
print("=" * 50)

print("1. Improves code reusability.")
print("2. Makes code flexible.")
print("3. Reduces code duplication.")
print("4. Makes programs easier to maintain.")
print("5. Supports dynamic method invocation.")

print("\nProgram completed successfully!")