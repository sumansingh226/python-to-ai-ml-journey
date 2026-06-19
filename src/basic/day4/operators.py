"""
=========================================================
OPERATORS IN PYTHON
=========================================================

What are Operators?
-------------------
Operators are symbols used to perform operations on
variables and values.

Why Do We Use Operators?
------------------------
1. To perform calculations.
2. To compare values.
3. To make decisions in programs.
4. To combine conditions.
5. To update variable values.

Types of Operators:
-------------------
1. Arithmetic Operators
2. Comparison Operators
3. Logical Operators
4. Assignment Operators
5. Membership Operators
6. Identity Operators
"""

# 1. ARITHMETIC OPERATORS
# Used for mathematical calculations.

a = 10
b= 3

print("Arithmetic operations")

print("addition : " ,  a+b)
print("Subtraction : " ,  a -b)
print("Multiplication : ", a*b)
print("division : " ,a /b)
print("Floor Division:", a // b)   
print("Modulus:", a % b)           
print("Power:", a ** b)            




# 2. COMPARISON OPERATORS
# Used to compare two values.
# Returns True or False.

print("=== Comparison Operators ===")

print("Equal:", a == b)                # False
print("Not Equal:", a != b)            # True
print("Greater Than:", a > b)          # True
print("Less Than:", a < b)             # False
print("Greater or Equal:", a >= b)     # True
print("Less or Equal:", a <= b)        # False

print()

#3 Assignment operator

# Used to assign and update values.

num = 10
num +=5
print("+=",num)
num -= 2
print("-= :", num)

num *=2
print("*= :", num)

num /= 2
print("/= :", num)        

print()

# 5. MEMBERSHIP OPERATORS
# Used to check if a value exists in a collection.
print("=== Membership Operators ===")

skills = ["Python", "AI", "ML"]

print("Python" in skills)
print("java" in skills)
print("java" not in skills)

# 6. IDENTITY OPERATORS
# Used to check whether two variables refer
# to the same object in memory.

list1 = [1, 2, 3]
list2 = list1
list3 = [1, 2, 3]

print("=== Identity Operators ===")
print(list1 is list2)
print(list1 is list3)

print(list1 is not list3) 