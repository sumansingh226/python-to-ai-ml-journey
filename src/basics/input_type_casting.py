"""
=========================================================
INPUT & TYPE CASTING IN PYTHON
=========================================================

What is input()?
----------------
input() is used to take input from the user through the keyboard.

Why Do We Use input()?
----------------------
1. To make programs interactive.
2. To get information from users.
3. To avoid hardcoding values.

Important:
----------
input() always returns a STRING (str).

What is Type Casting?
---------------------
Type casting means converting one data type into another.

Common Type Casting Functions:
------------------------------
str()   -> Convert to String
int()   -> Convert to Integer
float() -> Convert to Float
bool()  -> Convert to Boolean
"""

#  BASIC INPUT
name = input("Enter your name ")
print("\n Basic input example:")
print(f"Hello,{name}!")
print(type(name)) #input() return string
print()

#input of numbers 
age = input("Enter your gae :")
print("\n Age Example : ")
print(age)
print(type(age)) #still string
print()

#string to integer

age = int(age)
print("String to integer")
print(type(age))
print()

#string to float 

height = float(input("Enter your height : "))
print("\n string to float:")
print(type(height))
print()

#  INTEGER TO STRING
marks = 95

marks_str = str(marks)

print("Integer to String:")
print(marks_str)
print(type(marks_str))
print()

# FLOAT TO INTEGER
price = 99.99

price_int = int(price)

print("Float to Integer:")
print(price_int)
print(type(price_int))
print()

#BOOLEAN CONVERSION

print("Boolean Conversion:")

print(bool(1))      # True
print(bool(0))      # False
print(bool("Hi"))   # True
print(bool(""))     # False
