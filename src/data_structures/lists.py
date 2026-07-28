#list in python

"""
Lists in Python

What is a List?
A list is an ordered collection of items.
mutable (changeable) collection of items.
Think of a list as a container that can hold multiple values
inside a single variable.
Why do we use Lists?
- Store multiple values in one variable
- Manage collections of data
- Most commonly used data structure in Python
- Widely used in Data Science and AI/ML
"""

#command use functions 
# append()   -> Add item at end
# insert()   -> Add item at specific position
# remove()   -> Remove item by value
# pop()      -> Remove item by index
# sort()     -> Sort list
# reverse()  -> Reverse list
# copy()     -> Create copy of list
# clear()    -> Remove all items
# count()    -> Count occurrences
# index()    -> Find position of item


#creating a list 

skills = ["Python", "Sql", "Machine learning"]
numbers = [10,20,30,40]
mixed = ["Rahul",25,True,5.9]

print(skills)
print(numbers)
print(mixed)

# Accessing Elements (Indexing)

print(skills[0])
print(skills[1])
print(skills[-1])

# Slicing

print(numbers[0:2])
print(numbers[1::3])



# Length of List

print(len(skills))


#adding elements 

skills.append("JavaScript")
print(skills)

#inserting elements 

skills.insert(1,"Git")
print(skills)

# Removing Elements

skills.remove("Sql")
print(skills)

# Remove Last Element
skills.pop()
print(skills)

# Updating Elements

skills[0] = "Python Programming"

print(skills)

# Checking Existence

print("Git" in skills)

# Looping Through a List

for skill in skills:
    print(skill)

# Sorting

marks = [90, 70, 85, 60]
print("marks before sort : ",marks)
marks.sort()
print("sort ",marks)

# Reverse Sorting

marks.sort(reverse=True)

print(marks)


# Copying Lists

list1 = [1, 2, 3]

list2 = list1.copy()

print(list2)