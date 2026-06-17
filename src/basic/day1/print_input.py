# input() is used to take input from the user (keyboard)
# It always returns the value as a string (text)
name = input("Enter your name: ")

# print() is used to display output on the screen
# Here we are combining text + variable (name) to make a message
print("Welcome", name, "to AI/ML journey 🚀")

# =========================
# TYPES OF print() IN PYTHON
# =========================

# 1. Simple print (basic output)
print("Hello World")  
# Used to display simple text on screen

# 2. Printing multiple values
print("Name:", "Alice", "Age:", 20)  
# Prints multiple values separated by space by default

# 3. Printing a variable
name = "John"
print(name)  
# Prints the value stored in variable

# 4. Using sep parameter (separator)
print("Python", "AI", "ML", sep="-")  
# sep changes how values are separated

# 5. Using end parameter (end of line control)
print("Hello", end=" ")
print("World")  
# end=" " keeps output in same line

# 6. Using f-string (BEST and most used in AI/ML)
age = 22
print(f"My name is {name} and I am {age} years old")  
# f-string allows embedding variables inside text

# 7. Printing expressions (calculations)
print(5 + 3)  
print(10 * 2)  
# print can also evaluate and show results directly

