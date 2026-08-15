import random
import time

from algorithms import insertion_sort


def benchmark(size):
    records = [
        {"value": random.randint(1, 100000)}
        for _ in range(size)
    ]

    start = time.perf_counter()

    insertion_sort(records, "value")

    end = time.perf_counter()

    return end - start


sizes = [10, 500, 3000]

print("Insertion Sort Benchmark")
print("-------------------------")

for size in sizes:
    elapsed = benchmark(size)

    print(
        f"Size: {size:5d} | "
        f"Time: {elapsed:.6f} seconds"
    )