"""
heapq_demo.py

A practical introduction to Python's built-in heapq module.

heapq is useful for:
    - Priority queues
    - Finding the smallest/largest N items
    - Scheduling tasks
    - Maintaining a dynamically changing collection
    - Algorithms such as Dijkstra's shortest path

Python version:
    Python 3.8+
"""

import heapq


# 1. BASIC MIN-HEAP

def basic_heap_example():
    """Demonstrate the basic heap operations."""

    print("\n" + "=" * 60)
    print("1. BASIC MIN-HEAP")
    print("=" * 60)

    numbers = [5, 1, 8, 3, 2]

    # Convert the list into a heap.
    heapq.heapify(numbers)

    print("\nHeap:")
    print(numbers)

    # The smallest element is always at index 0.
    print("\nSmallest element:")
    print(numbers[0])

    # Remove the smallest element.
    smallest = heapq.heappop(numbers)

    print("\nRemoved:")
    print(smallest)

    print("Heap after pop:")
    print(numbers)


# 2. heappush()

def push_example():
    """Demonstrate adding elements to a heap."""

    print("\n" + "=" * 60)
    print("2. heappush()")
    print("=" * 60)

    heap = []

    heapq.heappush(heap, 10)
    heapq.heappush(heap, 3)
    heapq.heappush(heap, 7)
    heapq.heappush(heap, 1)

    print("\nHeap:")
    print(heap)

    print("\nSmallest:")
    print(heap[0])


# 3. heappop()

def pop_example():
    """Remove elements from a heap in priority order."""

    print("\n" + "=" * 60)
    print("3. heappop()")
    print("=" * 60)

    heap = [5, 1, 8, 3, 2]

    heapq.heapify(heap)

    print("\nRemoving elements:")

    while heap:
        value = heapq.heappop(heap)
        print(value)

    # Output:
    # 1
    # 2
    # 3
    # 5
    # 8


# 4. heappush() + heappop()

def push_pop_example():
    """Demonstrate heappushpop()."""

    print("\n" + "=" * 60)
    print("4. heappushpop()")
    print("=" * 60)

    heap = [2, 5, 8, 10]

    heapq.heapify(heap)

    # Add 1 and immediately remove the smallest value.
    result = heapq.heappushpop(heap, 1)

    print("\nRemoved:")
    print(result)

    print("Heap:")
    print(heap)


# 5. heapreplace()

def replace_example():
    """Demonstrate heapreplace()."""

    print("\n" + "=" * 60)
    print("5. heapreplace()")
    print("=" * 60)

    heap = [2, 5, 8, 10]

    heapq.heapify(heap)

    # Remove the smallest item first,
    # then add the new item.

    result = heapq.heapreplace(heap, 20)

    print("\nRemoved:")
    print(result)

    print("Heap:")
    print(heap)


# 6. nsmallest()

def nsmallest_example():
    """Find the N smallest values."""

    print("\n" + "=" * 60)
    print("6. nsmallest()")
    print("=" * 60)

    numbers = [50, 10, 80, 30, 20, 90, 40]

    smallest = heapq.nsmallest(
        3,
        numbers
    )

    print("\nThree smallest:")
    print(smallest)

    # Output:
    # [10, 20, 30]


# 7. nlargest()

def nlargest_example():
    """Find the N largest values."""

    print("\n" + "=" * 60)
    print("7. nlargest()")
    print("=" * 60)

    numbers = [50, 10, 80, 30, 20, 90, 40]

    largest = heapq.nlargest(
        3,
        numbers
    )

    print("\nThree largest:")
    print(largest)

    # Output:
    # [90, 80, 50]


# 8. PRIORITY QUEUE

def priority_queue_example():
    """
    Use heapq as a priority queue.

    Smaller priority number = higher priority.
    """

    print("\n" + "=" * 60)
    print("8. PRIORITY QUEUE")
    print("=" * 60)

    tasks = []

    heapq.heappush(
        tasks,
        (2, "Send email")
    )

    heapq.heappush(
        tasks,
        (1, "Fix production bug")
    )

    heapq.heappush(
        tasks,
        (3, "Write documentation")
    )

    heapq.heappush(
        tasks,
        (1, "Restart server")
    )

    print("\nTasks in priority order:")

    while tasks:
        priority, task = heapq.heappop(tasks)

        print(
            f"Priority {priority}: {task}"
        )


# 9. PRIORITY QUEUE WITH TIE-BREAKING

def priority_tie_example():
    """
    Use a counter to guarantee a stable ordering when
    two tasks have the same priority.
    """

    print("\n" + "=" * 60)
    print("9. PRIORITY QUEUE WITH TIE-BREAKING")
    print("=" * 60)

    tasks = []

    counter = 0

    def add_task(priority, task):
        nonlocal counter

        heapq.heappush(
            tasks,
            (priority, counter, task)
        )

        counter += 1

    add_task(1, "Task A")
    add_task(1, "Task B")
    add_task(2, "Task C")
    add_task(1, "Task D")

    print("\nProcessing tasks:")

    while tasks:
        priority, _, task = heapq.heappop(tasks)

        print(
            f"Priority {priority}: {task}"
        )


# 10. HEAP WITH OBJECTS / CUSTOM SORTING

def custom_key_example():
    """Use tuples to prioritize objects by a particular field."""

    print("\n" + "=" * 60)
    print("10. CUSTOM PRIORITY")
    print("=" * 60)

    students = [
        ("Alice", 85),
        ("Bob", 92),
        ("Charlie", 78),
        ("David", 95),
    ]

    heap = []

    # Store (score, name).
    # The score becomes the priority.

    for name, score in students:
        heapq.heappush(
            heap,
            (score, name)
        )

    print("\nStudents from lowest score to highest:")

    while heap:
        score, name = heapq.heappop(heap)

        print(
            f"{name}: {score}"
        )


# 11. FIND TOP N OBJECTS

def top_students_example():
    """Find the three students with the highest scores."""

    print("\n" + "=" * 60)
    print("11. TOP N OBJECTS")
    print("=" * 60)

    students = [
        {"name": "Alice", "score": 85},
        {"name": "Bob", "score": 92},
        {"name": "Charlie", "score": 78},
        {"name": "David", "score": 95},
        {"name": "Eva", "score": 88},
    ]

    top_students = heapq.nlargest(
        3,
        students,
        key=lambda student: student["score"]
    )

    print("\nTop three students:")

    for student in top_students:
        print(
            student["name"],
            student["score"]
        )


# 12. MERGE SORTED ITERABLES

def merge_example():
    """Merge multiple already-sorted iterables."""

    print("\n" + "=" * 60)
    print("12. merge()")
    print("=" * 60)

    first = [1, 4, 7]
    second = [2, 5, 8]
    third = [3, 6, 9]

    merged = heapq.merge(
        first,
        second,
        third
    )

    print("\nMerged values:")

    for value in merged:
        print(value, end=" ")

    print()


# 13. PRACTICAL EXAMPLE: SERVER TASKS

def server_task_example():
    """
    Simulate a server processing tasks according to priority.
    """

    print("\n" + "=" * 60)
    print("13. PRACTICAL EXAMPLE: SERVER TASKS")
    print("=" * 60)

    task_queue = []

    tasks = [
        (3, "Generate report"),
        (1, "Database backup"),
        (2, "Send notification"),
        (1, "Security scan"),
        (4, "Clean temporary files"),
    ]

    for priority, task in tasks:
        heapq.heappush(
            task_queue,
            (priority, task)
        )

    print("\nProcessing queue:")

    while task_queue:
        priority, task = heapq.heappop(task_queue)

        print(
            f"[Priority {priority}] {task}"
        )


# 14. HEAP VS SORTED

def heap_vs_sorted_example():
    """
    Show the difference between sorting everything and
    finding only the smallest N values.
    """

    print("\n" + "=" * 60)
    print("14. HEAP VS SORTED")
    print("=" * 60)

    numbers = [
        100, 5, 72, 18, 33,
        91, 2, 44, 67, 10
    ]

    # Sorting creates a complete sorted result.
    sorted_numbers = sorted(numbers)

    print("\nUsing sorted():")
    print(sorted_numbers)

    # heapq.nsmallest() only asks for the smallest N.
    smallest = heapq.nsmallest(
        3,
        numbers
    )

    print("\nUsing heapq.nsmallest(3):")
    print(smallest)


# 15. COMMON HEAP PATTERN

def common_pattern():
    """
    The most important heap pattern:

        heapify()
        heappush()
        heappop()

    This lets us maintain a collection where the smallest
    element is always easily accessible.
    """

    print("\n" + "=" * 60)
    print("15. COMMON HEAP PATTERN")
    print("=" * 60)

    numbers = [7, 2, 9, 1, 5]

    heapq.heapify(numbers)

    print("\nInitial heap:")
    print(numbers)

    heapq.heappush(numbers, 3)

    print("\nAfter adding 3:")
    print(numbers)

    smallest = heapq.heappop(numbers)

    print("\nRemoved smallest:")
    print(smallest)

    print("\nRemaining heap:")
    print(numbers)


# MAIN

def main():
    """Run all heapq demonstrations."""

    basic_heap_example()
    push_example()
    pop_example()
    push_pop_example()
    replace_example()
    nsmallest_example()
    nlargest_example()
    priority_queue_example()
    priority_tie_example()
    custom_key_example()
    top_students_example()
    merge_example()
    server_task_example()
    heap_vs_sorted_example()
    common_pattern()


if __name__ == "__main__":
    main()