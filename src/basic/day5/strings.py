

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