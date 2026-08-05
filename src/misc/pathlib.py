"""
pathlib Module in Python

What is pathlib?

pathlib is a built-in Python module used
to work with files and directories using
an object-oriented approach.

It is the modern replacement for os.path.

------------------------------------------------

Why do we use pathlib?

1. Create file paths easily.
2. Check if files exist.
3. Create directories.
4. Read and write files.
5. Navigate directories.
6. Find files using patterns.
7. Cross-platform compatibility.

------------------------------------------------

Import

from pathlib import Path
"""

from pathlib import Path


# Example 1 : Current Working Directory

path = Path.cwd()

print(path)

print()


# Example 2 : Home Directory

home = Path.home()

print(home)

print()


# Example 3 : Create a Path

file = Path("student.json")

print(file)

print()


# Example 4 : Check File Exists

print(file.exists())

print()

