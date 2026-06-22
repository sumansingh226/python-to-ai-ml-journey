"""
Loops in Python

What are Loops?
Loops are used to execute a block of code repeatedly.

Why do we use Loops?
- To avoid writing repetitive code
- To process collections of data
- To automate repetitive tasks
- To iterate through lists, strings, files, etc.

Types of Loops:
1. for loop
2. while loop
3. nested loops
4. break
5. continue
6. pass
7. range()
"""


#for loop 

print("For loop")
for i in range(5):
    print(i)

#for loop with list 
print("\nLooping through a list: ")
skills = ["Python", "AI","ML"]
for  skill in skills:
    print(skill)

#range 
print("\n using range(start, end)")

for i in range(1,6):
    print(i)

#  while loop
print("\n while loop")

count = 1
while count <=5:
   print(count)
   count += 1



 #break
print("\nBreak Example:")

for i in range(10):
    if i == 5:
        break

    print(i)

# Loop stops when i becomes 5


# 6. continue
print("\nContinue Example:")

for i in range(5):
    if i == 2:
        continue

    print(i)

# Skips 2


 # pass
print("\nPass Example:")

for i in range(3):
    if i == 1:
        pass

    print(i)


# 8. Nested Loops
print("\nNested Loops:")

for i in range(3):
    for j in range(3):
        print(f"i={i}, j={j}")


# 9. Loop through a string
print("\nString Loop:")

name = "Python"

for char in name:
    print(char)