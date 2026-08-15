
from algorithms import (
    insertion_sort,
    binary_search,
    linear_search,
    insertion_sort_count,
    binary_search_count,
    linear_search_count,
)


def check(name, actual, expected):
    if actual == expected:
        print(f"PASS: {name}")
    else:
        print(f"FAIL: {name}")
        print(f"Expected: {expected}")
        print(f"Got: {actual}")


# -------------------------
# INSERTION SORT
# -------------------------

records = [
    {"value": 5},
    {"value": 2},
    {"value": 4},
    {"value": 1},
]

insertion_sort(records, "value")

check(
    "insertion_sort",
    records,
    [
        {"value": 1},
        {"value": 2},
        {"value": 4},
        {"value": 5},
    ],
)


# -------------------------
# BINARY SEARCH
# -------------------------

records = [
    {"value": 10},
    {"value": 20},
    {"value": 30},
    {"value": 40},
    {"value": 50},
]

check(
    "binary_search first",
    binary_search(records, 10, "value"),
    0,
)

check(
    "binary_search middle",
    binary_search(records, 30, "value"),
    2,
)

check(
    "binary_search last",
    binary_search(records, 50, "value"),
    4,
)

check(
    "binary_search not found",
    binary_search(records, 99, "value"),
    None,
)


# -------------------------
# LINEAR SEARCH
# -------------------------

check(
    "linear_search first",
    linear_search(records, 10, "value"),
    0,
)

check(
    "linear_search middle",
    linear_search(records, 30, "value"),
    2,
)

check(
    "linear_search not found",
    linear_search(records, 99, "value"),
    None,
)


# -------------------------
# INSERTION SORT COUNT
# -------------------------

records = [
    {"value": 5},
    {"value": 2},
    {"value": 4},
]

sorted_records, count = insertion_sort_count(
    records,
    "value"
)

check(
    "insertion_sort_count sorting",
    sorted_records,
    [
        {"value": 2},
        {"value": 4},
        {"value": 5},
    ],
)

if isinstance(count, int) and count > 0:
    print("PASS: insertion_sort_count comparison count")
else:
    print("FAIL: insertion_sort_count comparison count")


# -------------------------
# BINARY SEARCH COUNT
# -------------------------

records = [
    {"value": 10},
    {"value": 20},
    {"value": 30},
    {"value": 40},
    {"value": 50},
]

index, count = binary_search_count(
    records,
    30,
    "value"
)

check(
    "binary_search_count index",
    index,
    2,
)

if isinstance(count, int) and count > 0:
    print("PASS: binary_search_count comparison count")
else:
    print("FAIL: binary_search_count comparison count")


# -------------------------
# LINEAR SEARCH COUNT
# -------------------------

index, count = linear_search_count(
    records,
    40,
    "value"
)

check(
    "linear_search_count index",
    index,
    3,
)

if count == 4:
    print("PASS: linear_search_count comparison count")
else:
    print(
        f"FAIL: linear_search_count comparison count "
        f"(got {count})"
    )


print()
print("Algorithm checks completed.")