"""
=========================================================
DATA TYPES IN PYTHON
=========================================================

What is a Data Type?
--------------------
A data type defines the kind of value a variable can store.

Why Do We Use Data Types?
-------------------------
1. To store different kinds of data.
2. To perform valid operations on data.
3. To help Python understand how to handle values.
4. To write clean and reliable programs.

Common Data Types:
------------------
str   -> Text
int   -> Whole Numbers
float -> Decimal Numbers
bool  -> True / False
list  -> Collection of items
tuple -> Fixed collection of items
set   -> Unique items
dict  -> Key-Value pairs
"""

# =========================================================
# 1. STRING (str)
# =========================================================
# Used to store text data.

name = "Rahul"

print("String Example:")
print(name)
print(type(name))
print()


# =========================================================
# 2. INTEGER (int)
# =========================================================
# Used to store whole numbers.

age = 25

print("Integer Example:")
print(age)
print(type(age))
print()


# =========================================================
# 3. FLOAT (float)
# =========================================================
# Used to store decimal numbers.

height = 5.9

print("Float Example:")
print(height)
print(type(height))
print()


# =========================================================
# 4. BOOLEAN (bool)
# =========================================================
# Used to store True or False values.

is_student = True

print("Boolean Example:")
print(is_student)
print(type(is_student))
print()


# =========================================================
# 5. LIST (list)
# =========================================================
# Used to store multiple items in order.
# Lists can be modified.

skills = ["Python", "SQL", "Machine Learning"]

print("List Example:")
print(skills)
print(type(skills))
print()


# =========================================================
# 6. TUPLE (tuple)
# =========================================================
# Used to store fixed data.
# Tuples cannot be modified.

coordinates = (10, 20)

print("Tuple Example:")
print(coordinates)
print(type(coordinates))
print()


# =========================================================
# 7. SET (set)
# =========================================================
# Used to store unique values.

numbers = {1, 2, 3, 4}

print("Set Example:")
print(numbers)
print(type(numbers))
print()


# =========================================================
# 8. DICTIONARY (dict)
# =========================================================
# Used to store data as key-value pairs.

student = {
    "name": "Rahul",
    "age": 25,
    "course": "AI/ML"
}

print("Dictionary Example:")
print(student)
print(type(student))
print()


# =========================================================
# CHECKING DATA TYPES
# =========================================================
# type() is used to check the data type of a variable.

print("Type Checking:")
print(type(name))
print(type(age))
print(type(height))
print(type(is_student))