"""
Virtual Environments (venv) in Python

What is a Virtual Environment?

A virtual environment (venv) is an isolated
Python environment for a project.

Each virtual environment has its own:

- Python interpreter
- Installed packages
- Package versions

Changes inside one virtual environment
do not affect other projects.

------------------------------------------------

Why do we use Virtual Environments?

1. Isolate project dependencies.
2. Avoid package version conflicts.
3. Keep projects independent.
4. Reproduce projects easily.
5. Standard practice in Python development.

------------------------------------------------

Without Virtual Environment

Project A
│
├── Django 4.2
└── NumPy 1.26

Project B
│
├── Django 5.0
└── NumPy 2.0

Conflict!

------------------------------------------------

With Virtual Environment

Project A
│
└── venv/
    ├── Django 4.2
    └── NumPy 1.26

Project B
│
└── venv/
    ├── Django 5.0
    └── NumPy 2.0

No conflicts.
"""