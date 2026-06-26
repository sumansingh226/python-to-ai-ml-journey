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

