# Lusbir

This library provides a Python integer range type -- the **lusbir** -- that is based on a different characterization of integer ranges than the characterization that built-in Python ranges are based on.

## Why?

This project wasn't really made with a practical use case in mind -- it was more for exploring a novel concept, and also for gaining some experience making and publishing a library.

That being said, if you think you'll find this useful, this _is_ a full-fledged library that can be installed and used in actual code. The public API is stable, though it currently leaves many details unspecified when it comes to the specific outputs of many methods.

## Installation

The library should work for any version of Python starting from Python 3.10, though it has only been tested on Python 3.11.1.

https://pypi.org/project/shape-warrior-t.lusbir/

`pip install shape-warrior-t.lusbir`

## How do lusbirs work?

(Built-in) Python ranges are specified by three integers: `start`, `stop`, and `step`. The numbers in a Python range start at `start`, and then increase by `step` until they reach `stop`, which is not included in the range.

Lusbirs are specified by four pieces of information: a **lower bound**, an **upper bound**, a **step**, and a **base**.

All numbers in a lusbir are between the lusbir's lower bound and upper bound, which can be any combination of inclusive and exclusive (unlike Python ranges, where `stop` is always exclusive).

Additionally, all numbers in a lusbir are of the form $n \times \mathrm{step} + \mathrm{base}$, where $n$ is an integer. This is like how all numbers in a Python range are of the form $n \times \mathrm{step} + \mathrm{start}$ for some integer $n$, but for lusbirs, $n$ can be negative -- instead of starting at 0, the starting value of $n$ is determined by the lower and upper bounds.

Just like Python ranges, the numbers in a lusbir increase by the step each time. This means that lusbirs with a positive step are ordered from low to high and lusbirs with a negative step are ordered from high to low, the same as Python ranges.

### Example: a lusbir with inclusive lower bound 0, exclusive upper bound 10, step 2, and base 1

We consider all numbers of the form $n \times \mathrm{step} + \mathrm{base}$, where $n$ is an integer -- in this case, all numbers of the form $2n + 1$ for some integer $n$:

$$\dotsc, -13, -11, -9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 11, 13, 15, \dotsc$$

Then we apply the bounds, keeping only the numbers between 0 (inclusive) and 10 (exclusive):

$$1, 3, 5, 7, 9$$

The end result, $[1, 3, 5, 7, 9]$, is the list of numbers that this lusbir represents.

### Example: a lusbir with exclusive lower bound 5, inclusive upper bound 55, step -10, and base 5

Take all numbers of the form $-10n + 5$ for some integer $n$:

$$\dotsc, 75, 65, 55, 45, 35, 25, 15, 5, -5, -15, -25, -35, -45, -55, -65, \dotsc$$

Keep only the numbers between 5 (exclusive) and 55 (inclusive):

$$55, 45, 35, 25, 15$$

We find that this lusbir represents the list $[55, 45, 35, 25, 15]$. Since the step is negative, the list is ordered from high to low.
