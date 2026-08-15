PRIORITY_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


def insertion_sort(records, key):
    for i in range(1, len(records)):
        current = records[i]
        j = i - 1

        while j >= 0 and records[j][key] > current[key]:
            records[j + 1] = records[j]
            j -= 1

        records[j + 1] = current

    return records


def binary_search(sorted_records, target_value, key):
    left = 0
    right = len(sorted_records) - 1

    while left <= right:
        mid = (left + right) // 2

        if sorted_records[mid][key] == target_value:
            return mid

        if sorted_records[mid][key] < target_value:
            left = mid + 1
        else:
            right = mid - 1

    return None


def linear_search(records, target_value, key):
    for i, record in enumerate(records):
        if record[key] == target_value:
            return i

    return None


def insertion_sort_count(records, key):
    comparisons = 0

    for i in range(1, len(records)):
        current = records[i]
        j = i - 1

        while j >= 0:
            comparisons += 1

            if records[j][key] <= current[key]:
                break

            records[j + 1] = records[j]
            j -= 1

        records[j + 1] = current

    return records, comparisons


def binary_search_count(sorted_records, target_value, key):
    comparisons = 0
    left = 0
    right = len(sorted_records) - 1

    while left <= right:
        mid = (left + right) // 2
        comparisons += 1

        if sorted_records[mid][key] == target_value:
            return mid, comparisons

        if sorted_records[mid][key] < target_value:
            left = mid + 1
        else:
            right = mid - 1

    return None, comparisons


def linear_search_count(records, target_value, key):
    comparisons = 0

    for i, record in enumerate(records):
        comparisons += 1

        if record[key] == target_value:
            return i, comparisons

    return None, comparisons