"""
itertools_demo.py

A practical introduction to Python's built-in itertools module.

itertools provides fast, memory-efficient iterator building blocks.
Most itertools functions are lazy: they produce values only when
requested instead of creating the entire result in memory.

Python version:
    Python 3.10+ recommended
"""

import itertools


# ============================================================
# 1. COMBINATORIC ITERATORS
# ============================================================

def combinatoric_examples():
    """Demonstrate product(), permutations(), and combinations()."""

    print("\n" + "=" * 60)
    print("1. COMBINATORIC ITERATORS")
    print("=" * 60)

    # --------------------------------------------------------
    # product()
    # --------------------------------------------------------
    # Cartesian product.
    # Equivalent to nested loops.
    product_result = itertools.product(
        ["A", "B"],
        [1, 2]
    )

    print("\nproduct():")
    print(list(product_result))

    # Output:
    # [('A', 1), ('A', 2), ('B', 1), ('B', 2)]

    # --------------------------------------------------------
    # permutations()
    # --------------------------------------------------------
    # Generates ordered arrangements.
    # Order matters.
    permutation_result = itertools.permutations(
        [1, 2, 3],
        2
    )

    print("\npermutations():")
    print(list(permutation_result))

    # Output:
    # [(1, 2), (1, 3), (2, 1),
    #  (2, 3), (3, 1), (3, 2)]

    # --------------------------------------------------------
    # combinations()
    # --------------------------------------------------------
    # Generates selections where order does not matter.
    combination_result = itertools.combinations(
        [1, 2, 3],
        2
    )

    print("\ncombinations():")
    print(list(combination_result))

    # Output:
    # [(1, 2), (1, 3), (2, 3)]


# ============================================================
# 2. TERMINATING ITERATORS
# ============================================================

def terminating_examples():
    """Demonstrate common terminating iterator functions."""

    print("\n" + "=" * 60)
    print("2. TERMINATING ITERATORS")
    print("=" * 60)

    # --------------------------------------------------------
    # chain()
    # --------------------------------------------------------
    # Combines multiple iterables into one sequence.

    result = itertools.chain(
        [1, 2],
        ["a", "b"],
        [True, False]
    )

    print("\nchain():")
    print(list(result))

    # Output:
    # [1, 2, 'a', 'b', True, False]

    # --------------------------------------------------------
    # islice()
    # --------------------------------------------------------
    # Similar to list slicing, but works with iterators.

    def number_generator():
        for number in range(100):
            yield number

    numbers = number_generator()

    sliced = itertools.islice(
        numbers,
        10,
        13
    )

    print("\nislice():")
    print(list(sliced))

    # Output:
    # [10, 11, 12]

    # --------------------------------------------------------
    # pairwise()
    # --------------------------------------------------------
    # Available from Python 3.10+.
    # Produces overlapping pairs.

    pairs = itertools.pairwise(
        [1, 2, 3, 4]
    )

    print("\npairwise():")
    print(list(pairs))

    # Output:
    # [(1, 2), (2, 3), (3, 4)]

    # --------------------------------------------------------
    # groupby()
    # --------------------------------------------------------
    # Groups CONSECUTIVE elements having the same key.
    #
    # Important:
    # groupby() does not automatically collect every matching
    # value throughout the entire iterable.
    #
    # Sorting by the key first is often necessary.

    people = [
        ("Alice", "Engineering"),
        ("Bob", "Engineering"),
        ("Charlie", "Sales"),
        ("David", "Sales"),
        ("Eva", "HR"),
    ]

    print("\ngroupby():")

    for department, employees in itertools.groupby(
        people,
        key=lambda person: person[1]
    ):
        print(department, list(employees))


# ============================================================
# 3. INFINITE ITERATORS
# ============================================================

def infinite_examples():
    """Demonstrate count(), cycle(), and repeat()."""

    print("\n" + "=" * 60)
    print("3. INFINITE ITERATORS")
    print("=" * 60)

    # --------------------------------------------------------
    # count()
    # --------------------------------------------------------
    # Generates:
    # 10, 12, 14, 16, 18, ...
    #
    # It never stops, so use next(), islice(), or a condition.

    counter = itertools.count(
        start=10,
        step=2
    )

    print("\ncount():")

    print(next(counter))
    print(next(counter))
    print(next(counter))
    print(next(counter))

    # Output:
    # 10
    # 12
    # 14
    # 16

    # --------------------------------------------------------
    # cycle()
    # --------------------------------------------------------
    # Repeats an iterable forever.

    cycler = itertools.cycle(
        ["ON", "OFF"]
    )

    print("\ncycle():")

    print(next(cycler))
    print(next(cycler))
    print(next(cycler))
    print(next(cycler))

    # Output:
    # ON
    # OFF
    # ON
    # OFF

    # --------------------------------------------------------
    # repeat()
    # --------------------------------------------------------
    # Repeats a value.
    #
    # If times is omitted, it repeats forever.

    repeated = itertools.repeat(
        "Python",
        3
    )

    print("\nrepeat():")
    print(list(repeated))

    # Output:
    # ['Python', 'Python', 'Python']


# ============================================================
# 4. FILTERING ITERATORS
# ============================================================

def filtering_examples():
    """Demonstrate filtering-related itertools functions."""

    print("\n" + "=" * 60)
    print("4. FILTERING ITERATORS")
    print("=" * 60)

    numbers = range(1, 11)

    # --------------------------------------------------------
    # compress()
    # --------------------------------------------------------
    # Selects elements according to a selector iterable.

    data = ["A", "B", "C", "D"]
    selectors = [True, False, True, False]

    result = itertools.compress(
        data,
        selectors
    )

    print("\ncompress():")
    print(list(result))

    # Output:
    # ['A', 'C']

    # --------------------------------------------------------
    # filterfalse()
    # --------------------------------------------------------
    # Opposite of filter().
    # Keeps elements for which the predicate is False.

    even_numbers = itertools.filterfalse(
        lambda x: x % 2 == 0,
        numbers
    )

    print("\nfilterfalse():")
    print(list(even_numbers))

    # Output:
    # [1, 3, 5, 7, 9]

    # --------------------------------------------------------
    # dropwhile()
    # --------------------------------------------------------
    # Drops elements while the condition is True.
    # Once it becomes False, everything else is returned.

    result = itertools.dropwhile(
        lambda x: x < 5,
        range(1, 10)
    )

    print("\ndropwhile():")
    print(list(result))

    # Output:
    # [5, 6, 7, 8, 9]

    # --------------------------------------------------------
    # takewhile()
    # --------------------------------------------------------
    # Takes elements while the condition is True.
    # Stops at the first False.

    result = itertools.takewhile(
        lambda x: x < 5,
        range(1, 10)
    )

    print("\ntakewhile():")
    print(list(result))

    # Output:
    # [1, 2, 3, 4]


# ============================================================
# 5. ACCUMULATION
# ============================================================

def accumulation_examples():
    """Demonstrate accumulate()."""

    print("\n" + "=" * 60)
    print("5. ACCUMULATION")
    print("=" * 60)

    # --------------------------------------------------------
    # accumulate()
    # --------------------------------------------------------
    # By default, produces running totals.

    numbers = [1, 2, 3, 4, 5]

    totals = itertools.accumulate(numbers)

    print("\naccumulate() - running total:")
    print(list(totals))

    # Output:
    # [1, 3, 6, 10, 15]

    # --------------------------------------------------------
    # accumulate() with a custom operation
    # --------------------------------------------------------

    products = itertools.accumulate(
        numbers,
        lambda x, y: x * y
    )

    print("\naccumulate() - running product:")
    print(list(products))

    # Output:
    # [1, 2, 6, 24, 120]


# ============================================================
# 6. ZIP-LIKE ITERATORS
# ============================================================

def zip_examples():
    """Demonstrate zip_longest()."""

    print("\n" + "=" * 60)
    print("6. ZIP-LIKE ITERATORS")
    print("=" * 60)

    names = ["Alice", "Bob", "Charlie"]
    scores = [90, 85]

    # --------------------------------------------------------
    # zip_longest()
    # --------------------------------------------------------
    # Continues until the longest iterable is exhausted.

    result = itertools.zip_longest(
        names,
        scores,
        fillvalue=0
    )

    print("\nzip_longest():")
    print(list(result))

    # Output:
    # [('Alice', 90), ('Bob', 85), ('Charlie', 0)]


# ============================================================
# 7. REPEATED ITERATION
# ============================================================

def repeated_iteration_examples():
    """Demonstrate repeat() with map()."""

    print("\n" + "=" * 60)
    print("7. REPEATED ITERATION")
    print("=" * 60)

    # repeat() can be useful when a function needs the same
    # argument multiple times.

    powers = map(
        pow,
        range(1, 6),
        itertools.repeat(2)
    )

    print("\nmap() + repeat():")
    print(list(powers))

    # Output:
    # [1, 4, 9, 16, 25]


# ============================================================
# 8. LAZY EVALUATION
# ============================================================

def lazy_evaluation_example():
    """
    Demonstrate why itertools is useful for large datasets.
    """

    print("\n" + "=" * 60)
    print("8. LAZY EVALUATION")
    print("=" * 60)

    # This generator can conceptually produce an enormous
    # number of values without storing them all in memory.

    def huge_numbers():
        number = 0

        while True:
            yield number
            number += 1

    numbers = huge_numbers()

    # Get only five values.
    first_five = itertools.islice(
        numbers,
        5
    )

    print("\nFirst five values:")
    print(list(first_five))

    # Output:
    # [0, 1, 2, 3, 4]

    print(
        "\nThe generator does not create all infinite values "
        "in memory."
    )


# ============================================================
# 9. PRACTICAL EXAMPLE
# ============================================================

def practical_example():
    """
    Practical example:
    Generate possible username combinations.
    """

    print("\n" + "=" * 60)
    print("9. PRACTICAL EXAMPLE")
    print("=" * 60)

    prefixes = ["dev", "admin"]
    numbers = ["01", "02", "03"]

    usernames = itertools.product(
        prefixes,
        numbers
    )

    print("\nPossible usernames:")

    for prefix, number in usernames:
        username = f"{prefix}{number}"
        print(username)


# ============================================================
# 10. COMBINING ITERTOOLS FUNCTIONS
# ============================================================

def combined_example():
    """
    Demonstrate how itertools functions can be combined
    to create an efficient processing pipeline.
    """

    print("\n" + "=" * 60)
    print("10. COMBINING ITERTOOLS")
    print("=" * 60)

    numbers = range(1, 1_000_000)

    # Pipeline:
    #
    # 1. Generate numbers lazily.
    # 2. Keep only even numbers.
    # 3. Take the first five.
    #
    # No list containing one million values is created.

    even_numbers = filter(
        lambda x: x % 2 == 0,
        numbers
    )

    first_five = itertools.islice(
        even_numbers,
        5
    )

    print("\nFirst five even numbers:")
    print(list(first_five))

    # Output:
    # [2, 4, 6, 8, 10]


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():
    """Run all demonstrations."""

    combinatoric_examples()
    terminating_examples()
    infinite_examples()
    filtering_examples()
    accumulation_examples()
    zip_examples()
    repeated_iteration_examples()
    lazy_evaluation_example()
    practical_example()
    combined_example()


if __name__ == "__main__":
    main()