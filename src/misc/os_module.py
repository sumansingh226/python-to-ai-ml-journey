"""
OS Module in Python

What is the os Module?

The os module provides functions to
interact with the operating system.

It allows you to:

- Work with files
- Work with directories
- Access environment variables
- Execute operating system commands
- Handle file paths

------------------------------------------------

Why do we use os Module?

1. Create directories.
2. Delete files and folders.
3. Rename files.
4. Get current working directory.
5. Check if files exist.
6. Read environment variables.
7. Build file paths.
8. Used in automation and AI/ML projects.

------------------------------------------------

Import

import os
"""

import os


# Example 1 : Current Working Directory

print(os.getcwd())

print()


# Example 2 : List Files and Folders

print(os.listdir())

print()


# Example 3 : Create Directory

directory = "demo_folder"

if not os.path.exists(directory):

    os.mkdir(directory)

    print("Folder Created")

else:

    print("Folder Already Exists")

print()


# Example 4 : Rename Directory

if os.path.exists("demo_folder"):

    os.rename("demo_folder", "python_folder")

    print("Folder Renamed")

print()


# Example 5 : Remove Empty Directory

if os.path.exists("python_folder"):

    os.rmdir("python_folder")

    print("Folder Deleted")

print()


# Example 6 : Check File Exists

print(os.path.exists("student.json"))

print()


# Example 7 : File or Directory

print(os.path.isfile("student.json"))

print(os.path.isdir("src"))

print()


# Example 8 : Join Paths

path = os.path.join("data", "train", "dataset.csv")

print(path)

print()


# Example 9 : Absolute Path

print(os.path.abspath("student.json"))

print()


# Example 10 : File Name

path = "/home/admin1/project/student.json"

print(os.path.basename(path))

print()


# Example 11 : Directory Name

print(os.path.dirname(path))

print()


# Example 12 : Split Path

directory, filename = os.path.split(path)

print(directory)

print(filename)

print()


# Example 13 : File Extension

name, extension = os.path.splitext("student.json")

print(name)

print(extension)

print()


# Example 14 : Environment Variable

print(os.getenv("HOME"))

print()


# Example 15 : Execute System Command

os.system("echo Hello from Python")