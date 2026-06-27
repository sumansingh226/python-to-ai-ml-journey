#file handling in python
"""
File Handling in Python

What is File Handling?

File handling is the process of creating,
reading, writing, updating, and deleting files.

Why do we use File Handling?

1. Store data permanently
2. Read data from files
3. Save logs
4. Save user information
5. Read datasets
6. Process CSV and text files

Without file handling,
all program data is lost after the program ends.
"""
# Open a file for reading
file = open("src/basic/day10/sample.txt", "r")
print(file.read())
file.close()

#open file for writing 
file = open("src/basic/day10/sampleWrite.txt","w")
file.write("\n Hello world")
file.close()

# Read line by line
file = open("sample.txt", "r")
for line in file:
    print(line)
file.close()


#read first line of file 

file = open("sample.txt", "r")
print(file.readline)
file.close()