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


# Example 3 : Copy File with Metadata

shutil.copy2(
    "source.txt",
    "copy_metadata.txt"
)

print("File Copied with metadata")


# Example 4 : Create Directory

Path("backup").mkdir(exist_ok=True)


# Example 5 : Copy File into Directory

shutil.copy(
    "source.txt",
    "backup"
)

print("Copied into backup folder")


# Example 6 : Copy Complete Directory

Path("dataset").mkdir(exist_ok=True)

Path("dataset/data.txt").write_text(
    "Training Data"
)


shutil.copytree(
    "dataset",
    "dataset_backup",
    dirs_exist_ok=True
)

print("Directory Copied")


# Example 7 : Move File

shutil.move(
    "copy.txt",
    "backup/copy.txt"
)

print("File Moved")


# Example 8 : Remove Directory

if Path("dataset_backup").exists():

    shutil.rmtree(
        "dataset_backup"
    )

print("Directory Removed")


# Example 9 : Create ZIP Archive

shutil.make_archive(
    "project_backup",
    "zip",
    "backup"
)

print("ZIP Created")


# Example 10 : Extract ZIP

shutil.unpack_archive(
    "project_backup.zip",
    "extracted"
)

print("ZIP Extracted")