"""
shutil Module in Python

What is shutil?

shutil stands for "shell utilities".

It is a built-in Python module used for
high-level file and directory operations.

------------------------------------------------

Why do we use shutil?

1. Copy files.
2. Copy complete directories.
3. Move files/folders.
4. Delete directories.
5. Create archives.
6. Extract archives.
7. Manage datasets and backups.

"""

import shutil
from pathlib import Path


# Example 1 : Create Sample Files

source = Path("source.txt")

source.write_text("Hello Python shutil")

print("Source file created")


# Example 2 : Copy File

shutil.copy(
    "source.txt",
    "copy.txt"
)

print("File Copied")

