"""
Instance Variables vs Class Variables

What is an Instance Variable?

An instance variable belongs to an object.

Every object has its own copy.

What is a Class Variable?

A class variable belongs to the class.

All objects share the same copy.
"""


# Example 1 : Instance Variables

class Student:

    def __init__(self, name, age):
        self.name = name
        self.age = age


student1 = Student("Suman", 24)
student2 = Student("Rahul", 22)

print(student1.name)
print(student2.name)

print(student1.age)
print(student2.age)


# Example 2 : Class Variable

class Employee:

    company = "OpenAI"

    def __init__(self, name):
        self.name = name


emp1 = Employee("Suman")
emp2 = Employee("Rahul")

print(emp1.company)
print(emp2.company)

print(Employee.company)

#example 3 class var
class Student: 
    grade = "11th"
    def __init__(self,name):
        self.name = name
        
stud1 = Student("suman")   
stud2 = Student("Raj")   
print("class var", stud1.name) 
print("class var",stud1.grade)
print("class var", stud2.name) 
print("class var",stud2.grade)



# Example 1 : Instance Variables

class Student:

    def __init__(self, name, age):
        self.name = name
        self.age = age


student1 = Student("Suman", 24)
student2 = Student("Rahul", 22)

print(student1.name)
print(student2.name)

print(student1.age)
print(student2.age)





# Example 3 : Different Objects

class Car:

    wheels = 4

    def __init__(self, brand, color):
        self.brand = brand
        self.color = color


car1 = Car("BMW", "Black")
car2 = Car("Audi", "White")

print(car1.brand)
print(car2.brand)

print(car1.color)
print(car2.color)

print(car1.wheels)
print(car2.wheels)
