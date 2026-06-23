
"""
Sets in Python

What is a Set?

A set is an unordered collection of unique items.

Think of a set as a collection that automatically
removes duplicate values.

Example:

numbers = {1, 2, 3, 4}

Why Do We Use Sets?

1. Store Unique Values
----------------------
Sets automatically remove duplicates.

Example:

numbers = {1, 2, 2, 3, 3, 4}

Result:

{1, 2, 3, 4}


2. Fast Searching
-----------------
Sets are optimized for checking whether
a value exists.

Example:

"Python" in skills


3. Remove Duplicates
--------------------
One of the most common real-world uses.

Example:

names = ["Rahul", "Amit", "Rahul"]

unique_names = set(names)

Result:

{"Rahul", "Amit"}


4. Mathematical Set Operations
------------------------------
Union
Intersection
Difference

Useful in data analysis and machine learning.


Key Characteristics

✓ Unordered
✓ Unique values only
✓ Mutable
✓ No indexing
✓ Fast lookups
✓ Cannot contain mutable objects like lists
"""

names = {"Suman" , "Raj","Suman"}
names2 = ["Suman" , "Raj","Suman"]
names2 = set(names2)
print(names,names2)

#check in set 
print("Suman" in names2)

# Duplicate Removal

data = {1, 2, 2, 3, 3, 4}

print(data)


# Length

skills = {"Python", "AI", "ML"}

numbers = {1, 2, 3, 4}

print(skills)
print(numbers)
print(len(skills))


#add item 
skills.add("Deep learning")

print(skills)

#add multiple items

skills.update(["Git", "Docker"])
print("Skills",skills)

#remove items 
skills.remove("Git")
print(skills)


#Discard items
# discard() removes an item from a set if it exists.

# If the item does not exist, Python does nothing and does not raise an error.
skills.discard("java")

print(skills)


# Membership Check

print("Python" in skills)

print("Java" in skills)


# Loop Through Set

for skill in skills:
    print(skill)

