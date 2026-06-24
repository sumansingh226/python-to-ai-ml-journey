"""
Modules and Packages in Python

What is a Module?

A module is a Python file containing code
(functions, variables, classes) that can be reused
in other Python files.

Why do we use Modules?

- Reuse code
- Organize projects
- Avoid duplication
- Use Python's built-in functionality
"""


#import entire module

import math

print(math.sqrt(25))
print(math.pi)

#import  specific functions


from math import sqrt,pi

print(sqrt(30))
print(pi)



# Import with alias

import math as m

print(m.sqrt(49))


# Built-in modules
import random

print(random.randint(1, 10))


# Another built-in module

import datetime

print(datetime.datetime.now())