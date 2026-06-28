#oops in python 
"""
Object-Oriented Programming (OOP)

What is OOP?

Object-Oriented Programming is a programming paradigm
that organizes code using objects and classes.

Instead of writing everything in functions,
we create objects that contain both data and behavior.

Why do we use OOP?

1. Better code organization
2. Code reusability
3. Easier maintenance
4. Real-world modeling
5. Used in large applications

Real-Life Example

Class = Car Blueprint

Object = BMW
Object = Audi
Object = Tesla

All cars share common features,
but each has different values.
"""


#create a class in python 

class Student:
    #method
    def greet(self):
        print("Welcome to Python class")

#creating objects

student1 = Student()
student2 = Student()

#calling methods 

student1.greet()
student2.greet()

"""
Class
-----
Blueprint or template.

Object
------
A real instance created from the class.

Attribute
---------
A variable inside a class.

Method
------
A function inside a class.

self
----
Represents the current object.

Example : 

Class
-----
Student

Objects
-------
Rahul
Amit
Priya

"""