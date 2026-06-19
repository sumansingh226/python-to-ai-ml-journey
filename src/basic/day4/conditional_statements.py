"""
Conditional Statements in Python

What are Conditional Statements?
Conditional statements allow a program to make decisions
based on conditions.

Why do we use them?
- To make decisions
- To control program flow
- To execute code only when conditions are met
"""


#if statement 

age = 20
if age>=18:
   print("You are eligible for vote")

#if-else 
age = 16
if age>=18:
   print("you can vote.")
else :
   print("you can't vote")

#if-else-if
marks = 65
if marks >= 90:
   print("A+")
elif marks >= 75:
   print("A")
elif marks >= 60:
   print("B")
elif marks >= 40:
   print("C")
else:
   print("failed")
    