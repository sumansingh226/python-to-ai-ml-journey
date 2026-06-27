"""
Exception Handling in Python

What is an Exception?

An exception is an error that occurs while
the program is running.

Without exception handling:
Program crashes.

With exception handling:
Program handles the error gracefully
and continues execution.

Why do we use Exception Handling?

1. Prevent program crashes
2. Handle unexpected errors
3. Improve user experience
4. Make applications more reliable
"""


# Example 1: Error without exception handling

# number = int(input("Enter a number: "))
# print(number)

# If user enters:
# hello

# Error:
# ValueError


# Example 2: try-except

try:
    number = int(input("Enter a number: "))
    print("You entered:", number)

except ValueError:
    print("Please enter a valid number")


# Example 3: Handling Division Error

try:
    result = 10 / 0
    print(result)

except ZeroDivisionError:
    print("Cannot divide by zero")


# Example 4: Multiple Exceptions

try:
    number = int(input("Enter a number: "))
    result = 100 / number

    print(result)

except ValueError:
    print("Invalid number")

except ZeroDivisionError:
    print("Division by zero is not allowed")


# Example 5: Generic Exception

try:
    x = 10
    y = 0

    print(x / y)

except Exception as e:
    print("Error:", e)


# Example 6: else Block

try:
    number = int(input("Enter a number: "))

except ValueError:
    print("Invalid input")

else:
    print("Valid input")
    print("Number:", number)


# Example 7: finally Block

try:
    result = 10 / 2

except ZeroDivisionError:
    print("Cannot divide by zero")

finally:
    print("This block always executes")


# Example 8: Raising Exception

age = -5

try:
    if age < 0:
        raise ValueError("Age cannot be negative")

except ValueError as e:
    print(e)


# Example 9: Real-world Example

try:
    username = input("Username: ")
    age = int(input("Age: "))

    print(f"{username} is {age} years old")

except ValueError:
    print("Age must be a number")