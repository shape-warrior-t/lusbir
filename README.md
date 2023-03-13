# Lusbir

[Github](https://github.com/shape-warrior-t/lusbir) | [PyPI](https://pypi.org/project/shape-warrior-t.lusbir/)

This library provides a Python integer range type -- the **lusbir** -- that is based on a different characterization of integer ranges than the characterization that built-in Python ranges are based on.

`pip install shape-warrior-t.lusbir`

This project wasn't really made with a practical use case in mind -- it was more for exploring a novel concept, and also for gaining some experience making and publishing a library. That being said, if you think you'll find this useful, feel free to install and use this library in your own code. The library should work for any version of Python starting from Python 3.10, though it has only been tested on Python 3.11.1.


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

In general, if a number is of the form $m \times \mathrm{step} + \mathrm{base}$ for some integer $m$, then it will be of the form $n \times \mathrm{-step} + \mathrm{base}$ for the integer $n = -m$. Thus, flipping the sign of a lusbir's step does not change which numbers it contains; it only reverses the lusbir's order.


## Lusbirs in code

### Introductory example

```python
>>> from lusbir import Lusbir
>>> for i in Lusbir('[)', 0, 30, 3, 2):
...     print(i)
...
2
5
8
11
14
17
20
23
26
29
```

We create a lusbir by passing some arguments to the `Lusbir` constructor, and we can iterate over the resulting `Lusbir` object just like a Python range.

The four numeric arguments specify, in order, the numeric lower bound, numeric upper bound, step, and base of the new lusbir. In this case, the lower bound is 0, the upper bound is 30, the step is 3, and the base is 2. Thus, the resulting lusbir represents the list of all numbers between 0 and 30 that are of the form $3n + 2$ -- in other words, the list $[2, 5, 8, 11, 14, 17, 20, 23, 26, 29]$, which matches the output that we got.

The initial string argument, meanwhile, is the new lusbir's _bound type_, representing whether the lower bound and the upper bound are inclusive or exclusive. The options for this argument are as follows:

| Bound type | Lower bound | Upper bound |
|------------|-------------|-------------|
| `'()'`     | exclusive   | exclusive   |
| `'(]'`     | exclusive   | inclusive   |
| `'[)'`     | inclusive   | exclusive   |
| `'[]'`     | inclusive   | inclusive   |

### General form

More generally, a call to the `Lusbir` constructor looks like this:

`Lusbir(bound_type, lb_num, ub_num, step, base)`

where `bound_type` is one of the four options from above, and `lb_num` (numeric lower bound), `ub_num` (numeric upper bound), `step`, and `base` are integers, with the restriction that `step` is nonzero. All arguments are positional-only.

There are abbreviated forms for the `Lusbir` constructor that do not specify all arguments, letting unspecified arguments take on their default values. Here are all of the ways to call the `Lusbir` constructor:
- `Lusbir(ub_num)`
- `Lusbir(lb_num, ub_num)`
- `Lusbir(lb_num, ub_num, step)`
- `Lusbir(lb_num, ub_num, step, base)`
- `Lusbir(bound_type, lb_num, ub_num)`
- `Lusbir(bound_type, lb_num, ub_num, step)`
- `Lusbir(bound_type, lb_num, ub_num, step, base)`

By default, `bound_type` is `'[)'`, `lb_num` is 0, `step` is 1, and `base` is 0. (`ub_num` must always be specified.)

### Big table of more examples

| Code                            | Bounds               | Form           | List represented                           |
|---------------------------------|----------------------|----------------|--------------------------------------------|
| `Lusbir('[)', 0, 10, 2, 1)`     | $0 \leq x < 10$      | $x = 2n + 1$   | $[1, 3, 5, 7, 9]$                          |
| `Lusbir('(]', 5, 55, -10, 5)`   | $5 < x \leq 55$      | $x = -10n + 5$ | $[55, 45, 35, 25, 15]$                     |
| `Lusbir('[]', -6, 6, 2)`        | $-6 \leq x \leq 6$   | $x = 2n$       | $[-6, -4, -2, 0, 2, 4, 6]$                 |
| `Lusbir('()', -6, 0)`           | $-6 < x < 0$         | $x = n$        | $[-5, -4, -3, -2, -1]$                     |
| `Lusbir(10)`                    | $0 \leq x < 10$      | $x = n$        | $[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]$           |
| `Lusbir(10, 15)`                | $10 \leq x < 15$     | $x = n$        | $[10, 11, 12, 13, 14]$                     |
| `Lusbir(10, 20, 2)`             | $10 \leq x < 20$     | $x = 2n$       | $[10, 12, 14, 16, 18]$                     |
| `Lusbir(10, 20, 2, 1)`          | $10 \leq x < 20$     | $x = 2n + 1$   | $[11, 13, 15, 17, 19]$                     |
| `Lusbir(10, 20, -2, 1)`         | $10 \leq x < 20$     | $x = -2n + 1$  | $[19, 17, 15, 13, 11]$                     |
| `Lusbir(0, 10, -1)`             | $0 \leq x < 10$      | $x = -n$       | $[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]$           |
| `Lusbir('(]', 0, 10, -1)`       | $0 < x \leq 10$      | $x = -n$       | $[10, 9, 8, 7, 6, 5, 4, 3, 2, 1]$          |
| `Lusbir('(]', 0, 10, -2)`       | $0 < x \leq 10$      | $x = -2n$      | $[10, 8, 6, 4, 2]$                         |
| `Lusbir(0, -10)`                | $0 \leq x < -10$     | $x = n$        | (empty list)                               |
| `Lusbir(10, 0, -1)`             | $10 \leq x < 0$      | $x = -n$       | (empty list)                               |
| `Lusbir('[]', -10, 10, 3)`      | $-10 \leq x \leq 10$ | $x = 3n$       | $[-9, -6, -3, 0, 3, 6, 9]$                 |
| `Lusbir('[]', -10, 10, 3, -10)` | $-10 \leq x \leq 10$ | $x = 3n - 10$  | $[-10, -7, -4, -1, 2, 5, 8]$               |
| `Lusbir('[]', -10, 10, 3, 10)`  | $-10 \leq x \leq 10$ | $x = 3n + 10$  | $[-8, -5, -2, 1, 4, 7, 10]$                |
| `Lusbir('()', -40, -20, 5, 1)`  | $-40 < x < -20$      | $x = 5n + 1$   | $[-39, -34, -29, -24]$                     |
| `Lusbir('()', 0, 40, 8, -1)`    | $0 < x < 40$         | $x = 8n - 1$   | $[7, 15, 23, 31, 39]$                      |


## Other exported items

Aside from the core `Lusbir` class, the Lusbir library also exports the `BoundType` type alias and the `Bound` and `LusbTuple` named tuple types.

`BoundType` is simply a type alias for <code>Literal['()',&nbsp;'(]',&nbsp;'[)',&nbsp;'[]']</code>, representing the four options for a lusbir's bound type.

The lower and upper bounds of a lusbir comprise both a numeric bound and an inclusive/exclusive status. In the Lusbir library, they are modelled by `Bound` objects, which are named tuples with the form <code>Bound(number:&nbsp;int,&nbsp;inclusive:&nbsp;bool)</code>. For example, <code>Bound(0,&nbsp;True)</code> represents an inclusive bound of 0, while <code>Bound(100,&nbsp;False)</code> represents an exclusive bound of 100. Both lower bounds and upper bounds use the same class -- there is nothing that keeps track of whether a bound is a lower bound or an upper bound.

The four pieces of information that characterize a lusbir -- the lower bound (lbound), upper bound (ubound), step, and base -- can be grouped into a **lusb tuple** $(\mathrm{lbound}, \mathrm{ubound}, \mathrm{step}, \mathrm{base})$. These are modelled in the Lusbir library by `LusbTuple` objects, which are named tuples with the form <code>LusbTuple(lbound:&nbsp;Bound,&nbsp;ubound:&nbsp;Bound,&nbsp;step:&nbsp;int,&nbsp;base:&nbsp;int)</code>. For example, a lusbir with inclusive lower bound 0, exclusive upper bound 30, step 3, and base 2 has the lusb tuple <code>LusbTuple(Bound(0,&nbsp;True),&nbsp;Bound(30,&nbsp;False),&nbsp;3,&nbsp;2)</code>.

A lusbir's lusb tuple can be obtained through its `lusb_tuple` property, and a lusbir can be created from a given lusb tuple using `Lusbir.from_lusb_tuple`:

```python
>>> from lusbir import Bound, LusbTuple, Lusbir
>>> Lusbir('[)', 0, 30, 3, 2).lusb_tuple
LusbTuple(lbound=Bound(number=0, inclusive=True), ubound=Bound(number=30, inclusive=False), step=3, base=2)
>>> lusbir = Lusbir.from_lusb_tuple(LusbTuple(Bound(0, True), Bound(30, False), 3, 2))
>>> lusbir
Lusbir('[)', 0, 30, 3, 2)
>>> list(lusbir)
[2, 5, 8, 11, 14, 17, 20, 23, 26, 29]
```

There are a few reasons one might want to work with lusb tuples:
- Equality for lusb tuples has stricter criteria than equality for lusbirs. Two lusbirs -- for example, <code>Lusbir('(]',&nbsp;20,&nbsp;50,&nbsp;10,&nbsp;5)</code> and <code>Lusbir('[)',&nbsp;25,&nbsp;55,&nbsp;10,&nbsp;25)</code> -- can represent the same list (in this case, $[25, 35, 45]$), but have different values for the lower bound, upper bound, step, and/or base. In this case, the lusbirs will compare equal, but their lusb tuples will not.
- Unpacking a lusb tuple is an easy way of getting all of the information that specifies a lusbir:
```python
>>> from lusbir import Lusbir
>>> lusbir = Lusbir('(]', 0, 20, -2)
>>> (lb_num, lb_incl), (ub_num, ub_incl), step, base = lusbir.lusb_tuple
>>> print(lb_incl, ub_incl, lb_num, ub_num, step, base)
False True 0 20 -2 0
```
- If you already have booleans denoting whether the lower/upper bounds of a lusbir are inclusive, there's no need to convert the boolean inclusivities to a bound type when using `Lusbir.from_lusb_tuple`.


## Other `Lusbir` functionality

A lusbir's lower bound, upper bound, step, and base can be accessed through its `lbound`, `ubound`, `step`, and `base` properties, which have the same values as the corresponding properties on the lusbir's lusb tuple.

```python
>>> from lusbir import Lusbir
>>> lusbir = Lusbir('(]', 0, 20, -2)
>>> lusbir.lbound
Bound(number=0, inclusive=False)
>>> lusbir.ubound
Bound(number=20, inclusive=True)
>>> lusbir.step
-2
>>> lusbir.base
0
```

The `to_range` instance method and the `Lusbir.from_range` static method allow for conversions between lusbirs and Python ranges (note that conversions may be lossy):

```python
>>> from lusbir import Lusbir
>>> Lusbir(0, 40, 8, 2).to_range()
range(2, 42, 8)
>>> Lusbir.from_range(range(2, 42, 8))
Lusbir('[)', 2, 42, 8, 2)
```

Most importantly, `Lusbir` is a subclass of `collections.abc.Sequence`, and implements the same functionality that `range` implements -- `__getitem__`, `__hash__`, `__len__`, `count`, `index`, etc.

Here are all of the public constructors, properties, and methods of the `Lusbir` class (`lr` represents an instance of the class):
- `Lusbir(ub_num: int, /) -> Lusbir`
- `Lusbir(lb_num: int, ub_num: int, step: int = 1, base: int = 0, /) -> Lusbir`
- `Lusbir(bound_type: BoundType, lb_num: int, ub_num: int, step: int = 1, base: int = 0, /) -> Lusbir`
- `Lusbir.from_lusb_tuple(lusb_tuple: LusbTuple, /) -> Lusbir`
- `lr.lbound: Bound`
- `lr.ubound: Bound`
- `lr.step: int`
- `lr.base: int`
- `lr.lusb_tuple: LusbTuple`
- `lr.__eq__(other, /) -> bool`
- `lr.__getitem__(index: int, /) -> int`
- `lr.__getitem__(slice_: slice, /) -> Lusbir`
- `lr.__hash__() -> int`
- `lr.__iter__() -> Iterator[int]`
- `lr.__repr__() -> str`
- `Lusbir.from_range(r: range, /) -> Lusbir`
- `lr.to_range() -> range`
- `lr.__bool__() -> bool`
- `lr.__contains__(x: int, /) -> bool`
- `lr.__len__() -> int`
- `lr.__reversed__() -> Iterator[int]`
- `lr.count(x: int, /) -> int`
- `lr.index(x: int, /) -> int`


## Misc
- I currently have no plans to further maintain or update the code for this library. If I do make changes to this library, it will be published as a new version, conforming to [SemVer](https://semver.org/).
- Still, if you spot any bugs, typos, or other problems in the code, tests, or documentation, please let me know via email: `bl.swt1@gmail.com`.
- If you manage to find some amazing use case for this library not already covered by built-in Python ranges, I would love to hear about it.
- Thanks for viewing and reading about this project!
