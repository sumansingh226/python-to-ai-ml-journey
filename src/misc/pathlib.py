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


# Example 5 : File or Directory

print(file.is_file())

print(Path("src").is_dir())

print()


# Example 6 : Create Directory

folder = Path("demo_folder")

folder.mkdir(exist_ok=True)

print("Folder Created")

print()


# Example 7 : Create Nested Directories

nested = Path("data/train/images")

nested.mkdir(parents=True, exist_ok=True)

print("Nested Folders Created")

print()


# Example 8 : Write Text File

text_file = Path("sample.txt")

text_file.write_text("Hello Python")

print("File Written")

print()


# Example 9 : Read Text File

content = text_file.read_text()

print(content)

print()


# Example 10 : File Name

print(text_file.name)

print()


# Example 11 : File Stem

print(text_file.stem)

print()


# Example 12 : File Extension

print(text_file.suffix)

print()


# Example 13 : Parent Directory

print(text_file.parent)

print()


# Example 14 : Absolute Path

print(text_file.resolve())

print()


# Example 15 : List Files

current = Path(".")

for item in current.iterdir():

    print(item)

print()


# Example 16 : Find Python Files

for file in Path(".").glob("*.py"):

    print(file)

print()


# Example 17 : Recursive Search

for file in Path(".").rglob("*.py"):

    print(file)

print()


# Example 18 : Delete File

temp = Path("temp.txt")

temp.write_text("Temporary File")

temp.unlink()

print("File Deleted")