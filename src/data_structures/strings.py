

#strings in python 

"""
Strings in Python

What is a String?
A string is a sequence of characters enclosed in
single quotes ('') or double quotes ("").

Why do we use Strings?
- Store text data
- User names
- Messages
- File names
- Data processing
- NLP and AI applications
"""


#len()
# Returns the total number of characters/items in an object.
# Used to count the length of strings, lists, tuples, etc.

#upper()
# Converts all characters in a string to uppercase.
# Used when you want text in capital letters.

#lower()
# Converts all characters in a string to lowercase.
# Useful for case-insensitive comparisons.

#title()
# Converts the first letter of each word to uppercase.
# Commonly used for formatting names and titles.

#capitalize()
# Converts the first character of the string to uppercase.
# Makes the rest of the string lowercase.

#strip()
# Removes leading and trailing whitespace from a string.
# Useful for cleaning user input.

#replace()
# Replaces one substring with another substring.
# Used to modify or update text.

#split()
# Splits a string into a list using a separator.
# Useful for processing CSV data, names, and sentences.

#startswith()
# Checks whether a string begins with a specific value.
# Returns True or False.

#endswith()
# Checks whether a string ends with a specific value.
# Returns True or False.

#find()
# Returns the index of the first occurrence of a substring.
# Returns -1 if the value is not found.

#count()
# Counts how many times a substring appears in a string.
# Useful for frequency checks.

#join()
# Combines elements of an iterable into a single string.
# Commonly used to merge lists into text.

#isalpha()
# Checks whether all characters are alphabetic letters.
# Returns True if only letters are present.



#creating strings 

name = "Raj"
city =  "Delhi"

print(name)
print(city)

#type of string 
print(type(name))


#indexing - Accessing individual characters

language = "Python"

print(language[0])
print(language[1])
print(language[-1])

#slicing - Extract part of the string 

print(language[0:3])
print(language[2:5])
print(language[:4])
print(language[4:])


# len()-String length
print(len(language))


#strings methods 

text = "Python ai ml"
print("\n\nnormal text : \n",text)
print("upper",text.upper())
print("lower",text.lower())
print("title",text.title())
print("capitalize", text.capitalize())


# Remove spaces

name = " Chandan "
print("\n\n normal",name)

print("stripe",name.strip())

#replace 
str = "i love java"
print("\n\n str",str)
print("replace : ", str.replace("java", "Python"))

# Check contents

text = "Python"
print(text.startswith("Py"))
print(text.endswith("on"))


# String concatenation

first_name = "Rahul"
last_name = " Sharma"
full_name = first_name +  last_name

print(full_name)


# f-strings (Recommended)

name = "Rahul"
age = 25

print(f"my name is {name} and i am {age}  years old.")


# Loop through a string

for char in "Python":
    print(char)


# Membership operators

text = "Machine learning "
print("Machine" in text)
print("java" in text)
print("java"  not in (text))


# Escape characters
print("Hello\nWorld")
print("Python\tAI\tML")
print("He said \"Hello\"")





# 1. Print the first character of your name

name = "raj"
print(name[:1])
# 2. Print the last character of your name

print(name[-1:])
# 3. Count the length of your name

print(len(name))
# 4. Convert your name to uppercase

print(name.upper())
# 5. Replace a word in a sentence
print(name.replace("raj","my name is raj"))
# 6. Reverse a string using slicing
print(name[::-1])
# 7. Check if "Python" exists in a string
str = "This is python"
print("python" in str)
# 8. Count vowels in a string
text = "Artificial Intelligence"

vowel_count = 0
for char in text.lower():
    if char in "aeiou":
        vowel_count += 1
print("Number of vowels :", vowel_count)

#practice question