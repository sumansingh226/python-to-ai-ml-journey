"""
datetime Module in Python

What is datetime?

The datetime module is used to work with
dates and times.

It allows you to:

- Get the current date and time
- Create custom dates
- Format dates
- Parse date strings
- Perform date calculations

------------------------------------------------

Why do we use datetime?

1. Store timestamps.
2. Calculate age.
3. Measure time differences.
4. Format dates.
5. Parse user input.
6. Log events.
7. Work with AI/ML datasets.

------------------------------------------------

Import

from datetime import datetime, date, time, timedelta
"""


from datetime import datetime, date, time, timedelta



# Example 1 : Current Date & Time
now = datetime.now()

print(now)

print()



# Example 2 : Current Date
today = date.today()

print(today)

print()



# Example 3 : Current Time
current_time = datetime.now().time()

print(current_time)

print()



# Example 4 : Create Custom Date
birthday = date(2002, 6, 15)

print(birthday)

print()



# Example 5 : Create Custom DateTime
meeting = datetime(2026, 8, 15, 10, 30, 0)

print(meeting)

print()



# Example 6 : Individual Components
print(now.year)
print(now.month)
print(now.day)
print(now.hour)
print(now.minute)
print(now.second)

print()



# Example 7 : Format Date
formatted = now.strftime("%d-%m-%Y")

print(formatted)

print()



# Example 8 : Format Time
formatted = now.strftime("%H:%M:%S")

print(formatted)

print()



# Example 9 : Custom Format
formatted = now.strftime("%A, %d %B %Y")

print(formatted)

print()



# Example 10 : Parse Date String
text = "25-12-2026"

parsed = datetime.strptime(text, "%d-%m-%Y")

print(parsed)

print()



# Example 11 : Add Days
future = now + timedelta(days=10)

print(future)

print()



# Example 12 : Subtract Days
past = now - timedelta(days=30)

print(past)

print()



# Example 13 : Difference Between Dates
start = date(2026, 1, 1)

end = date(2026, 12, 31)

difference = end - start

print(difference.days)

print()



# Example 14 : Calculate Age
birth = date(2002, 6, 15)

today = date.today()

age = today.year - birth.year

print(age)

print()



# Example 15 : Timestamp
print(datetime.now().timestamp())