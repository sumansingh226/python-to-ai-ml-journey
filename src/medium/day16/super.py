"""
super() in Python

What is super()?

super() is a built-in function that allows a child class
to access the methods and constructor of its parent class.

Why do we use super()?

1. Reuse parent class code.
2. Avoid duplicate code.
3. Call the parent constructor.
4. Extend parent functionality.

Real-Life Example

Parent
------
Person

Child
-----
Student

Every student is also a person.

Instead of writing Person's code again,
we reuse it using super().
"""


# ==========================================
# Example 1 : Calling Parent Method
# ==========================================

class Animal:

    def eat(self):
        print("Animal is eating")


class Dog(Animal):

    def bark(self):
        print("Dog is barking")

    def show(self):

        # Call Parent Method
        super().eat()

        print("Inside Child Class")


dog = Dog()

dog.show()


"""
Output

Animal is eating
Inside Child Class
"""


# ==========================================
# Example 2 : Parent Constructor
# ==========================================

class Person:

    def __init__(self, name):
        self.name = name

        print("Person Constructor")


class Student(Person):

    def __init__(self, name, age):

        # Call Parent Constructor
        super().__init__(name)

        self.age = age

        print("Student Constructor")


student = Student("Suman", 24)

print(student.name)
print(student.age)


"""
Output

Person Constructor
Student Constructor

Suman
24
"""


# ==========================================
# Example 3 : Without super()
# ==========================================

class Vehicle:

    def __init__(self, brand):
        self.brand = brand


class Car(Vehicle):

    def __init__(self, brand, model):

        # Parent constructor NOT called

        self.model = model


car = Car("BMW", "X5")

# print(car.brand)

"""
AttributeError

brand was never created because
Vehicle.__init__() was not called.
"""


# ==========================================
# Example 4 : Using super()
# ==========================================

class Vehicle:

    def __init__(self, brand):
        self.brand = brand


class Car(Vehicle):

    def __init__(self, brand, model):

        super().__init__(brand)

        self.model = model


car = Car("BMW", "X5")

print(car.brand)
print(car.model)


"""
Output

BMW
X5
"""


# ==========================================
# Example 5 : Parent + Child Method
# ==========================================

class Employee:

    def work(self):
        print("Employee is working")


class Developer(Employee):

    def work(self):

        super().work()

        print("Developer is writing Python code")


developer = Developer()

developer.work()


"""
Output

Employee is working
Developer is writing Python code
"""


# ==========================================
# Example 6 : AI/ML Example
# ==========================================

class Model:

    def __init__(self, name):
        self.name = name

    def train(self):
        print("Training Model")


class NeuralNetwork(Model):

    def __init__(self, name, layers):

        super().__init__(name)

        self.layers = layers

    def show(self):
        print(self.name)
        print(self.layers)


model = NeuralNetwork("ResNet", 50)

model.train()

model.show()