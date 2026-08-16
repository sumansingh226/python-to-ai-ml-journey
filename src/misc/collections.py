"""
collections Module

The collections module provides specialized
container data types.

Main tools:

Counter
defaultdict
deque
namedtuple
OrderedDict
ChainMap

GA4-style examples are included.
"""

from collections import (
    Counter,
    defaultdict,
    deque,
    namedtuple,
    OrderedDict,
    ChainMap
)


# ============================================================
# 1. COUNTER
# ============================================================

"""
Counter

Definition:
Counter counts how many times each value
appears in an iterable.

Useful for:
- Frequency counting
- Categories
- Events
- Text analysis
- GA4 metrics
"""

pages = [
    "home",
    "products",
    "home",
    "about",
    "products",
    "home",
    "contact"
]

page_count = Counter(pages)

print("Page count:")
print(page_count)

print()


# ============================================================
# 2. COUNTER.most_common()
# ============================================================

"""
most_common()

Returns the most frequently occurring items.
"""

print("Most common pages:")
print(page_count.most_common())

print()

print("Top 2 pages:")
print(page_count.most_common(2))

print()


# ============================================================
# 3. COUNTER WITH WORDS
# ============================================================

text = "python python java python java ai"

words = text.split()

word_count = Counter(words)

print("Word frequency:")
print(word_count)

print()


# ============================================================
# 4. COUNTER.update()
# ============================================================

counter = Counter(["Python", "Python", "Java"])

counter.update(["Python", "AI"])

print("Updated counter:")
print(counter)

print()


# ============================================================
# 5. COUNTER.subtract()
# ============================================================

counter.subtract(["Python"])

print("After subtract:")
print(counter)

print()


# ============================================================
# 6. COUNTER GA4 EXAMPLE
# ============================================================

traffic_sources = [
    "google",
    "google",
    "facebook",
    "google",
    "direct",
    "facebook",
    "instagram",
    "google",
    "direct"
]

source_count = Counter(traffic_sources)

print("GA4 Traffic Sources:")
print(source_count)

print()

print("Top traffic sources:")
print(source_count.most_common(3))

print()


# ============================================================
# 7. DEFAULTDICT
# ============================================================

"""
defaultdict

Definition:
defaultdict automatically creates a default
value when a key does not exist.
"""

scores = defaultdict(list)

scores["Suman"].append(90)
scores["Suman"].append(85)
scores["Rahul"].append(80)

print("Scores:")
print(scores)

print()


# ============================================================
# 8. DEFAULTDICT WITH INTEGER
# ============================================================

visitors = defaultdict(int)

visitors["January"] += 4200
visitors["February"] += 4500
visitors["January"] += 500

print("Monthly visitors:")
print(visitors)

print()


# ============================================================
# 9. DEFAULTDICT GA4 EXAMPLE
# ============================================================

monthly_sources = defaultdict(list)

monthly_sources["January"].append(4200)
monthly_sources["January"].append(4500)

monthly_sources["February"].append(4800)
monthly_sources["February"].append(5100)

print("Monthly source data:")
print(monthly_sources)

print()


# ============================================================
# 10. DEQUE
# ============================================================

"""
deque

Definition:
deque means double-ended queue.

It allows fast insertion and removal
from both ends.
"""

numbers = deque([1, 2, 3, 4])

numbers.append(5)

numbers.appendleft(0)

print("Deque:")
print(numbers)

print()


# ============================================================
# 11. REMOVE FROM DEQUE
# ============================================================

numbers.pop()

numbers.popleft()

print("After removing:")
print(numbers)

print()


# ============================================================
# 12. DEQUE ROTATE
# ============================================================

numbers = deque([1, 2, 3, 4, 5])

numbers.rotate(2)

print("Rotated:")
print(numbers)

print()


# ============================================================
# 13. GA4 RECENT VISITORS
# ============================================================

"""
deque is useful when we only want to keep
the most recent N records.
"""

recent_visitors = deque(maxlen=5)

recent_visitors.append(4200)
recent_visitors.append(4500)
recent_visitors.append(4700)
recent_visitors.append(5000)
recent_visitors.append(5200)

print("Recent visitors:")
print(recent_visitors)

recent_visitors.append(5500)

print("After new data:")
print(recent_visitors)

print()


# ============================================================
# 14. NAMEDTUPLE
# ============================================================

"""
namedtuple

Definition:
Creates tuple-like objects where values
can be accessed using meaningful names.
"""

Visitor = namedtuple(
    "Visitor",
    ["date", "visitors", "sessions"]
)

record = Visitor(
    "2026-08-01",
    4500,
    5200
)

print("Visitor record:")
print(record)

print()

print("Date:", record.date)

print("Visitors:", record.visitors)

print("Sessions:", record.sessions)

print()


# ============================================================
# 15. ORDEREDDICT
# ============================================================

"""
OrderedDict

Definition:
A dictionary designed for operations where
ordering behavior matters.

Modern Python dicts already preserve insertion
order, so OrderedDict is less important than
it was in older Python versions.
"""

data = OrderedDict()

data["January"] = 4200
data["February"] = 4500
data["March"] = 4800

print("Ordered data:")
print(data)

print()


# ============================================================
# 16. MOVE OrderedDict ITEM
# ============================================================

data.move_to_end("January")

print("After moving January:")
print(data)

print()


# ============================================================
# 17. CHAINMAP
# ============================================================

"""
ChainMap

Definition:
Combines multiple dictionaries into one
logical view.
"""

default_config = {
    "theme": "light",
    "language": "en",
    "limit": 100
}

user_config = {
    "theme": "dark",
    "limit": 50
}

config = ChainMap(
    user_config,
    default_config
)

print("Configuration:")
print(config)

print()

print("Theme:", config["theme"])

print("Language:", config["language"])

print("Limit:", config["limit"])

print()


# ============================================================
# 18. COUNTER MATHEMATICAL OPERATIONS
# ============================================================

website_a = Counter({
    "google": 100,
    "facebook": 50,
    "direct": 30
})

website_b = Counter({
    "google": 80,
    "facebook": 70,
    "instagram": 40
})

print("Combined:")
print(website_a + website_b)

print()

print("Common:")
print(website_a & website_b)

print()

print("Maximum:")
print(website_a | website_b)

print()


# ============================================================
# 19. GA4 WEEKLY EVENT COUNTS
# ============================================================

events = [
    "page_view",
    "page_view",
    "session_start",
    "page_view",
    "purchase",
    "page_view",
    "session_start",
    "purchase",
    "page_view"
]

event_count = Counter(events)

print("GA4 event counts:")
print(event_count)

print()

print("Top events:")
print(event_count.most_common())

print()