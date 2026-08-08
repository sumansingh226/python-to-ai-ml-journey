"""
pathlib Module in Python

What is pathlib?

pathlib is a built-in Python module used
to work with files and directories.

It provides an object-oriented way to
handle file paths.

------------------------------------------------

Why do we use pathlib?

1. Work with files and directories.
2. Create folders.
3. Check whether files exist.
4. Read and write files.
5. Build paths easily.
6. Make code cleaner.
7. Works across operating systems.

------------------------------------------------

Main Class

Path

Import:

from pathlib import Path
"""

from pathlib import Path


# ==========================================
# Example 1 : Current Directory
# ==========================================

current_directory = Path.cwd()

print(current_directory)

print()


# ==========================================
# Example 2 : Create a Path
# ==========================================

file_path = Path("student.json")

print(file_path)

print()


# ==========================================
# Example 3 : Check if Path Exists
# ==========================================

print(file_path.exists())

print()


# ==========================================
# Example 4 : Check File
# ==========================================

print(file_path.is_file())

print()


# ==========================================
# Example 5 : Check Directory
# ==========================================

directory = Path("src")

print(directory.is_dir())

print()


# ==========================================
# Example 6 : Create Directory
# ==========================================

data_folder = Path("data")

data_folder.mkdir(exist_ok=True)

print("Directory created")

print()


# ==========================================
# Example 7 : Create Nested Directories
# ==========================================

dataset_folder = Path("data") / "train" / "images"

dataset_folder.mkdir(parents=True, exist_ok=True)

print(dataset_folder)

print()


# ==========================================
# Example 8 : Create File
# ==========================================

file = Path("data/example.txt")

file.write_text("Hello Python")

print("File created")

print()


# ==========================================
# Example 9 : Read File
# ==========================================

content = file.read_text()

print(content)

print()


# ==========================================
# Example 10 : File Name
# ==========================================

print(file.name)

print()


# ==========================================
# Example 11 : File Extension
# ==========================================

print(file.suffix)

print()


# ==========================================
# Example 12 : File Stem
# ==========================================

print(file.stem)

print()


# ==========================================
# Example 13 : Parent Directory
# ==========================================

print(file.parent)

print()


# ==========================================
# Example 14 : Build Paths
# ==========================================

dataset = Path("data") / "train" / "dataset.csv"

print(dataset)

print()


# ==========================================
# Example 15 : List Files
# ==========================================

for item in Path("data").iterdir():

    print(item)

print()


# ==========================================
# Example 16 : Find Python Files
# ==========================================

for python_file in Path(".").glob("*.py"):

    print(python_file)

print()


# ==========================================
# Example 17 : Find Files Recursively
# ==========================================

for python_file in Path(".").rglob("*.py"):

    print(python_file)

print()


# ==========================================
# Example 18 : Rename File
# ==========================================

old_file = Path("data/example.txt")

new_file = Path("data/python.txt")

if old_file.exists():

    old_file.rename(new_file)

    print("File renamed")

print()


# ==========================================
# Example 19 : Delete File
# ==========================================

if new_file.exists():

    new_file.unlink()

    print("File deleted")

print()


# ==========================================
# Example 20 : AI/ML Dataset Example
# ==========================================

dataset_path = Path("datasets")

dataset_path.mkdir(exist_ok=True)

for file in dataset_path.glob("*.csv"):

    print("Dataset:", file)