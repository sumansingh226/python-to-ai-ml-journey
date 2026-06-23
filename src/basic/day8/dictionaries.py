#Dictionaries in Python

"""
Dictionaries in Python

What is a Dictionary?

A dictionary is a collection of data stored as
key-value pairs.

Think of it like a real dictionary:

Word      -> Meaning
Name      -> Rahul
Age       -> 25

Key       -> Value

Why do we use Dictionaries?

- Store related data together
- Fast data lookup
- Represent real-world objects
- Used heavily in APIs and JSON
- Very common in AI/ML and Data Science

Key Characteristics

✓ Key-Value pairs
✓ Mutable (changeable)
✓ Ordered (Python 3.7+)
✓ Keys must be unique
✓ Values can be duplicated
"""


# Creating Dictionary

student = {
    "name": "Rahul",
    "age": 25,
    "city": "Delhi"
}

print(student)

#access values 
print(student["name"])
print(student["age"])


#using get()
print("city of student :", student.get("city"))

#add a new key 

student["course"] = "AI/M"

#update value

student["age"]=26

print(student)

#remove item 
student.pop("city")

print(student)

#check key exist

print("name" in student)
print("salary" in student)

# Length

print(len(student))

#loop through keys

for key in student:
    print(key)


# Dictionary Methods

print(student.keys())

print(student.values())

print(student.items())


#copy Dictionary
student_copy = student.copy()
print(student_copy)

# Nested Dictionary

employees = {
    "emp1": {
        "name": "Rahul",
        "age": 25
    },
    "emp2": {
        "name": "Amit",
        "age": 30
    }
}

print(employees)

print(employees["emp1"]["name"])