"""
REGULAR EXPRESSIONS (re)

The re module is used to work with
patterns inside strings.

Common uses:

1. Search text
2. Find patterns
3. Extract information
4. Validate text
5. Replace text
6. Split text
7. Clean data

Import:
    import re
"""

import re


# 1. SEARCH

text = "Python is powerful"

result = re.search("Python", text)

print(result)

print()


# 2. SEARCH + GROUP

text = "My age is 24"

result = re.search(r"\d+", text)

if result:
    print(result.group())

print()


# 3. FINDALL

text = "Python 100 Java 200 C++ 300"

numbers = re.findall(r"\d+", text)

print(numbers)

print()


# 4. FIND ALL WORDS

text = "Python is easy to learn"

words = re.findall(r"\w+", text)

print(words)

print()


# 5. MATCH

text = "Python"

result = re.match(r"Python", text)

print(result)

print()


# 6. FULLMATCH

text = "Python"

result = re.fullmatch(r"Python", text)

print(result)

print()


# 7. SPLIT

text = "Python,Java,C++,Go"

languages = re.split(",", text)

print(languages)

print()


# 8. SUB

text = "Python is difficult"

result = re.sub(
    "difficult",
    "easy",
    text
)

print(result)

print()


# 9. DIGITS

text = "Order 123 costs 500"

numbers = re.findall(r"\d+", text)

print(numbers)

print()


# 10. WORD CHARACTERS

text = "Python_123"

result = re.findall(r"\w+", text)

print(result)

print()


# 11. WHITESPACE

text = "Python   is   awesome"

result = re.findall(r"\S+", text)

print(result)

print()


# 12. EMAIL EXTRACTION

text = """
Contact:
rahul@gmail.com
suman@yahoo.com
admin@example.com
"""

emails = re.findall(
    r"[\w.-]+@[\w.-]+\.\w+",
    text
)

print(emails)

print()


# 13. PHONE NUMBER

text = "Call me at 9876543210"

phone = re.findall(
    r"\b\d{10}\b",
    text
)

print(phone)

print()


# 14. URL

text = """
Visit https://example.com
or https://python.org
"""

urls = re.findall(
    r"https?://\S+",
    text
)

print(urls)

print()


# 15. DATE

text = """
2026-01-15
2026-05-20
2026-08-15
"""

dates = re.findall(
    r"\d{4}-\d{2}-\d{2}",
    text
)

print(dates)

print()


# 16. GA4-STYLE DATA

ga4_log = """
2026-08-01 visitors=4500
2026-08-08 visitors=5200
2026-08-15 visitors=6100
2026-08-22 visitors=5800
"""

visitor_counts = re.findall(
    r"visitors=(\d+)",
    ga4_log
)

print(visitor_counts)

print()


# 17. CONVERT EXTRACTED VALUES TO INTEGER

visitor_counts = [
    int(value)
    for value in visitor_counts
]

print(visitor_counts)

print()


# 18. EXTRACT DATE + VISITORS TOGETHER

pattern = r"(\d{4}-\d{2}-\d{2}) visitors=(\d+)"

records = re.findall(
    pattern,
    ga4_log
)

print(records)

print()


# 19. CREATE OBJECTS FROM EXTRACTED DATA

ga4_data = []

for date, visitors in records:

    ga4_data.append({
        "date": date,
        "visitors": int(visitors)
    })

print(ga4_data)

print()


# 20. CLEAN TEXT

text = "Python    is     very    useful"

clean_text = re.sub(
    r"\s+",
    " ",
    text
)

print(clean_text)