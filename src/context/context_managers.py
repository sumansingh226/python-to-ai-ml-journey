"""
Context Managers (with Statement) in Python

What is a Context Manager?

A context manager is an object that
automatically manages resources.

It acquires a resource before a block
of code executes and releases it after
the block finishes.

------------------------------------------------

Why do we use Context Managers?

1. Automatically close files.
2. Prevent resource leaks.
3. Write cleaner code.
4. Handle exceptions safely.
5. Used with files, databases, locks,
   sockets, and AI/ML resources.

------------------------------------------------

Syntax

with expression as variable:
    # Code Block
"""


# Example 1 : Without with

file = open("sample.txt", "r")

content = file.read()

print(content)

file.close()


print()


# Example 2 : With Statement

with open("sample.txt", "r") as file:

    content = file.read()

    print(content)


"""
The file is automatically closed.
"""


print()


# Example 3 : Writing to a File

with open("sample.txt", "w") as file:

    file.write("Hello Python")


print("Data Written")


print()


# Example 4 : Appending Data

with open("sample.txt", "a") as file:

    file.write("\nLearning Context Managers")


print("Data Appended")


print()


# Example 5 : Reading Line by Line

with open("sample.txt", "r") as file:

    for line in file:

        print(line.strip())


print()


# Example 6 : Exception Handling

try:

    with open("sample.txt", "r") as file:

        print(file.read())

except FileNotFoundError:

    print("File Not Found")


print()


# Example 7 : Multiple Context Managers

with open("sample.txt", "r") as source, \
     open("copy.txt", "w") as destination:

    destination.write(source.read())


print("File Copied")


print()


# Example 8 : Custom Context Manager

class Database:

    def __enter__(self):

        print("Database Connected")

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        print("Database Closed")


with Database() as db:

    print("Running Query")


print()


# Example 9 : AI/ML Example

with open("dataset.csv", "r") as dataset:

    print("Dataset Opened")

    # Process dataset here

print("Dataset Closed")


print()


# Example 10 : Check File Closed

with open("sample.txt", "r") as file:

    print(file.closed)

print(file.closed)