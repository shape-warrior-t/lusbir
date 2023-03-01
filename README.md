# Lusbir

[Github](https://github.com/shape-warrior-t/lusbir) | [PyPI](https://pypi.org/project/shape-warrior-t.lusbir/)

This library provides a Python integer range type -- the **lusbir** -- that is based on a different characterization of integer ranges than the characterization that built-in Python ranges are based on.


## Why?

This project wasn't really made with a practical use case in mind -- it was more for exploring a novel concept, and also for gaining some experience making and publishing a library.

That being said, if you think you'll find this useful, this _is_ a full-fledged library that can be installed and used in actual code. The public API is stable, though it currently leaves many details unspecified when it comes to the specific outputs of many methods.


## Installation

The library should work for any version of Python starting from Python 3.10, though it has only been tested on Python 3.11.1.

`pip install shape-warrior-t.lusbir`


## How do lusbirs work?

(Built-in) Python ranges are specified by three integers: `start`, `stop`, and `step`. The numbers in a Python range start at `start`, and then increase by `step` until they reach `stop`, which is not included in the range.

Lusbirs are specified by four pieces of information: a **lower bound**, an **upper bound**, a nonzero **step**, and a **base**.

All numbers in a lusbir are between the lusbir's lower bound and upper bound, which can be any combination of inclusive and exclusive (unlike Python ranges, where `stop` is always exclusive).

Additionally, all numbers in a lusbir are of the form $n \times \mathrm{step} + \mathrm{base}$, where $n$ is an integer. This is like how all numbers in a Python range are of the form $n \times \mathrm{step} + \mathrm{start}$ for some integer $n$, but for lusbirs, $n$ can be negative -- instead of starting at 0, the starting value of $n$ is determined by the lower and upper bounds.

Just like Python ranges, we go from one element of a lusbir to the next by adding the step. This means that lusbirs with a positive step are ordered from low to high and lusbirs with a negative step are ordered from high to low, the same as Python ranges.

### Example: a lusbir with inclusive lower bound 0, exclusive upper bound 10, step 2, and base 1

We consider all numbers of the form $n \times \mathrm{step} + \mathrm{base}$, where $n$ is an integer -- in this case, all numbers of the form $2n + 1$ for some integer $n$:

$$\dotsc, -5, -3, -1, 1, 3, 5, 7, 9, 11, 13, 15, \dotsc$$

Then we apply the bounds, keeping only the numbers between 0 (inclusive) and 10 (exclusive):

$$\dotsc, -5, -3, -1, \boxed{1, 3, 5, 7, 9}, 11, 13, 15, \dotsc$$

$$\downarrow$$

$$1, 3, 5, 7, 9$$

The end result, $[1, 3, 5, 7, 9]$, is the list of numbers that this lusbir represents.

### Example: a lusbir with exclusive lower bound 5, inclusive upper bound 55, step -10, and base 5

Take all numbers of the form $-10n + 5$ for some integer $n$:

$$\dotsc, 75, 65, 55, 45, 35, 25, 15, 5, -5, -15, -25, \dotsc$$

Keep only the numbers between 5 (exclusive) and 55 (inclusive):

$$\dotsc, 75, 65, \boxed{55, 45, 35, 25, 15}, 5, -5, -15, -25, \dotsc$$

$$\downarrow$$

$$55, 45, 35, 25, 15$$

We find that this lusbir represents the list $[55, 45, 35, 25, 15]$. Since the step is negative, the list is ordered from high to low.


## Actually using the library

First, let's create the example lusbirs from the previous section.

### First example

```python
>>> from lusbir import Lusbir
>>> for i in Lusbir('[)', 0, 10, 2, 1):
...     print(i)
...
1
3
5
7
9
```

By passing the integer arguments 0, 10, 2, and 1 to the `Lusbir` standard constructor, we create a lusbir with lower bound 0, upper bound 10, step 2, and base 1. The **bound type**, `'[)'`, indicates that the lower bound is _inclusive_ and that the upper bound is _exclusive_. As previously mentioned, this lusbir represents the list $[1, 3, 5, 7, 9]$, and as expected, iterating over the lusbir gives us the numbers 1, 3, 5, 7, and 9.

### Second example

```python
>>> from lusbir import Lusbir
>>> for i in Lusbir('(]', 5, 55, -10, 5):
...     print(i)
...
55
45
35
25
15
```

This time, the created lusbir has lower bound 5, upper bound 55, step -10, and base 5. The bound type `'(]'` indicates that the lower bound is _exclusive_ and the upper bound is _inclusive_.

Aside from `'[)'` and `'(]'`, the other bound types are `'[]'`, which indicates that both the lower bound and the upper bound are _inclusive_, and `'()'`, which indicates that both the lower bound and the upper bound are _exclusive_. This mirrors the standard mathematical notation for inclusive/exclusive intervals: all of the numbers in `Lusbir('[)', lb_num, ub_num, step, base)` are in the interval $[\mathrm{lb{\textunderscore}num}, \mathrm{ub{\textunderscore}num})$, all of the numbers in `Lusbir('(]', lb_num, ub_num, step, base)` are in the interval $(\mathrm{lb{\textunderscore}num}, \mathrm{ub{\textunderscore}num}]$, etc.

### Short forms

We don't always have to specify all five arguments each time.

If we omit the bound type, it will default to `'[)'`:

```python
>>> list(Lusbir(1, 11, 2, 1))  # 1 <= x < 11, x = 2n + 1
[1, 3, 5, 7, 9]
```

We can omit the final argument -- the base -- and have it default to 0:

```python
>>> list(Lusbir('[]', 0, 50, 10))  # 0 <= x <= 50, x = 10n
[0, 10, 20, 30, 40, 50]
>>> list(Lusbir(5, 55, -10))  # 5 <= x < 55, x = -10n
[50, 40, 30, 20, 10]
```

We can omit the final two arguments -- the step and the base -- and have them default to 1 and 0, respectively:

```python
>>> list(Lusbir('()', -5, 5))  # -5 < x < 5
[-4, -3, -2, -1, 0, 1, 2, 3, 4]
>>> list(Lusbir(-5, 5))  # -5 <= x < 5
[-5, -4, -3, -2, -1, 0, 1, 2, 3, 4]
```

Lastly, we can provide only one argument -- the numeric upper bound -- and get a lusbir with bound type `'[)'`, lower bound 0, step 1, and base 0:
```python
>>> list(Lusbir(10))
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```
