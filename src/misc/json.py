"""
JSON in Python

What is JSON?

JSON stands for JavaScript Object Notation.

It is a lightweight data-interchange format
used to store and exchange data.

JSON is:

- Human-readable
- Easy to write
- Easy to parse
- Language independent

------------------------------------------------

Why do we use JSON?

1. Store structured data.
2. Exchange data between applications.
3. Send and receive API responses.
4. Store configuration files.
5. Save AI/ML datasets.

------------------------------------------------

Python Module

import json
"""

import json



# Example 1 : Python Dictionary to JSON String
student = {
    "name": "Suman",
    "age": 24,
    "city": "Delhi"
}

json_data = json.dumps(student)

print(json_data)

print(type(json_data))

print()



# Example 2 : JSON String to Python Dictionary
json_string = '{"name":"Rahul","age":25,"city":"Mumbai"}'

student = json.loads(json_string)

print(student)

print(type(student))

print()



# Example 3 : Write JSON to File
student = {
    "name": "Amit",
    "age": 22,
    "course": "Python"
}

with open("student.json", "w") as file:

    json.dump(student, file, indent=4)

print("JSON written successfully.")

print()



# Example 4 : Read JSON File
with open("student.json", "r") as file:

    data = json.load(file)

print(data)

print(type(data))

print()



# Example 5 : Pretty Print JSON
employee = {
    "id": 101,
    "name": "Suman",
    "salary": 80000
}

print(json.dumps(employee, indent=4))

print()



# Example 6 : Sort Keys
data = {
    "city": "Delhi",
    "age": 24,
    "name": "Suman"
}

print(json.dumps(data, indent=4, sort_keys=True))

print()



# Example 7 : List of Dictionaries
students = [

    {
        "name": "Rahul",
        "age": 22
    },

    {
        "name": "Suman",
        "age": 24
    }

]

print(json.dumps(students, indent=4))

print()



# Example 8 : Boolean and Null
data = {
    "isStudent": True,
    "marks": None
}

print(json.dumps(data, indent=4))

print()



# Example 9 : AI/ML Dataset
dataset = [

    {
        "image": "cat.jpg",
        "label": "Cat"
    },

    {
        "image": "dog.jpg",
        "label": "Dog"
    }

]

with open("dataset.json", "w") as file:

    json.dump(dataset, file, indent=4)

print("Dataset Saved")

print()



# Example 10 : Read AI/ML Dataset
with open("dataset.json", "r") as file:

    dataset = json.load(file)

for item in dataset:

    print(item["image"], "->", item["label"])