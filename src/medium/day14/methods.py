"""
Class Variables in Python

What is a Class Variable?

A class variable is a variable that belongs to the class,
not to any individual object.

Only one copy of a class variable exists in memory,
and all objects of that class share it.

Why do we use Class Variables?

1. Store common data shared by all objects.
2. Save memory by avoiding duplicate values.
3. Maintain consistent information across all objects.
4. Easily update a value for every object.

Examples of Class Variables

Student
-------
school = "ABC School"

Employee
--------
company = "Google"

Car
---
wheels = 4

BankAccount
-----------
bank_name = "State Bank"

Every object created from the class shares these values.
"""


# Example 1 : Basic Class Variable

class Student:

    # Class Variable
    school = "ABC School"

    def __init__(self, name):
        self.name = name


student1 = Student("Suman")
student2 = Student("Rahul")

print(student1.school)
print(student2.school)
print(Student.school)


# Output
# ABC School
# ABC School
# ABC School


"""
Explanation

There is only ONE copy of 'school'.

student1
      \
       \
        -----> school = "ABC School"
       /
student2

Both objects access the same variable.
"""


# Example 2 : Updating a Class Variable

class Employee:

    company = "OpenAI"

    def __init__(self, name):
        self.name = name


emp1 = Employee("Suman")
emp2 = Employee("Rahul")

print(emp1.company)
print(emp2.company)

print()

Employee.company = "Google"

print(emp1.company)
print(emp2.company)

print(Employee.company)


# Output
# OpenAI
# OpenAI
#
# Google
# Google
# Google


"""
Explanation

Changing the class variable using the class name
updates it for every object because they all share
the same variable.
"""


# Example 3 : Accessing Class Variable

class Car:

    wheels = 4

    def __init__(self, brand):
        self.brand = brand


car1 = Car("BMW")
car2 = Car("Audi")

print(car1.wheels)
print(car2.wheels)
print(Car.wheels)


# Output
# 4
# 4
# 4


# Example 4 : Object Creates Its Own Variable

class Mobile:

    company = "Samsung"

    def __init__(self, model):
        self.model = model


mobile1 = Mobile("S24")
mobile2 = Mobile("A55")

print(mobile1.company)
print(mobile2.company)

print()

mobile1.company = "Apple"

print(mobile1.company)
print(mobile2.company)
print(Mobile.company)


# Output
# Samsung
# Samsung
#
# Apple
# Samsung
# Samsung


"""
Explanation

mobile1.company = "Apple"

does NOT change the class variable.

Instead, Python creates a NEW instance variable
called 'company' for mobile1.

Now:

mobile1 -> company = Apple

mobile2 -> uses class variable (Samsung)

Mobile -> company = Samsung
"""


# Example 5 : Memory Representation

"""
Student Class

school = "ABC School"

        ▲
        │
  -----------------
  │               │
student1      student2
name=Suman    name=Rahul

Both objects share:
school = "ABC School"

Each object has its own:
name
"""


# Example 6 : AI/ML Example

class NeuralNetwork:

    framework = "PyTorch"

    def __init__(self, model_name):
        self.model_name = model_name


model1 = NeuralNetwork("ResNet")

model2 = NeuralNetwork("VGG16")

print(model1.framework)
print(model2.framework)

print(model1.model_name)
print(model2.model_name)


# Example 7 : Best Practice

class Student:

    school = "ABC School"      # Class Variable

    def __init__(self, name, age):
        self.name = name       # Instance Variable
        self.age = age         # Instance Variable


student = Student("Suman", 24)

print(student.school)
print(student.name)
print(student.age)


"""
Class Variable vs Instance Variable

Class Variable
--------------
Belongs to the class

Created inside class

Shared by all objects

Only one copy exists

Accessed using:
ClassName.variable
or
object.variable


Instance Variable
-----------------
Belongs to an object

Created using self

Every object has its own copy

Different values for different objects

Accessed using:
self.variable
or
object.variable


Memory Trick

Class Variable
--------------
One value
Shared by everyone

Instance Variable
-----------------
One value
Per object
"""


# Interview Question

class Student:

    school = "ABC School"

    def __init__(self, name):
        self.name = name


student1 = Student("Suman")
student2 = Student("Rahul")

student1.school = "XYZ School"

print(student1.school)
print(student2.school)
print(Student.school)

# Output
# XYZ School
# ABC School
# ABC School

"""
Why?

student1.school creates an instance variable.

It does NOT modify the class variable.

The class variable remains unchanged.
"""