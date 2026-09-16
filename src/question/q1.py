a = [[]] * 3

print("Initial list:")
print(a) 

a[1].append(1)
print('after')
print(a) 


# 2. The Proof: Check their memory addresses
# id() returns the unique memory address for an object
print("Memory address of a[0]:", id(a[0]))
print("Memory address of a[1]:", id(a[1]))
print("Memory address of a[2]:", id(a[2]))


print("Are a[0] and a[1] the exact same list?", a[0] is a[1]) 


# 3. The Mutation
# Let's add a value to the FIRST list only

# 4. The Result
print("List after appending to a[0]:")
print(a)
# Output: [['Python'], ['Python'], ['Python']]

