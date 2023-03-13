"""This module provides lusbirs -- integer ranges characterized by a lower bound, upper bound, step, and base.

A lusbir represents the list of all numbers between the lower and upper bounds that are of the form
    n * step + base
for some integer n. Lower and upper bounds can be any combination of inclusive and exclusive.
Numbers are ordered such that (a * step + base) comes before (b * step + base) if and only if a < b --
lusbirs with a positive step are in ascending order, and lusbirs with a negative step are in descending order.
"""

__all__ = ['Bound', 'BoundType', 'LusbTuple', 'Lusbir']

from collections.abc import Iterator, Sequence
from typing import Literal, NamedTuple, TypeAlias, final, overload


class Bound(NamedTuple):
    """A lower or upper bound in a lusbir."""
    number: int
    inclusive: bool


class LusbTuple(NamedTuple):
    """A tuple of the four pieces of information that characterize a lusbir.

    Note that lusb tuples may have a step of 0, but lusbirs may not.
    Lusb tuples with a step of 0 do not represent valid lusbirs.
    """
    lbound: Bound
    ubound: Bound
    step: int
    base: int


# region lusbir construction helper functions

def _lusb_tuple_to_range(lusb_tuple: LusbTuple, /) -> range:
    """Return a Python range that represents the same list as a lusbir with the given lusb tuple."""

    (lb_num, lb_incl), (ub_num, ub_incl), step, base = lusb_tuple

    if step > 0:
        inclusive_start_bound = lb_num if lb_incl else lb_num + 1
        exclusive_stop_bound = ub_num + 1 if ub_incl else ub_num
    else:
        inclusive_start_bound = ub_num if ub_incl else ub_num - 1
        exclusive_stop_bound = lb_num - 1 if lb_incl else lb_num

    # Let the "progress" of an integer x be the real number r such that x = r * step + base.
    # Denoting the progress of the inclusive start bound with a
    # and the progress of the exclusive stop bound with b,
    # a number n with integer progress p is in the lusbir if and only if
    # a <= p < b -- or, in other words, iff p >= a and not p >= b.
    #
    # The first number with integer progress p >= a is (ceil(a) * step + base);
    # the first number with integer progress p >= b is (ceil(b) * step + base).
    # These can be the start and stop values for `range`.
    #
    # (The progress of the stop value does not actually need to be an integer --
    # in fact, the exclusive stop bound is a perfectly good stop value.
    # However, using a number with integer progress for the stop value gives us the elegant property that
    # the number of items in the range is exactly ((stop - start) / step),
    # except in the special case where `stop` "comes before" `start`,
    # in which case the range will be empty instead of containing a negative number of items.)
    # #

    start = _ceil_progress(inclusive_start_bound, step, base)
    stop = _ceil_progress(exclusive_stop_bound, step, base)
    return range(start, stop, step)


def _ceil_progress(x: int, step: int, base: int, /) -> int:
    """Expressing x as (r * step + base) for some real number r, return (ceil(r) * step + base)."""
    # Derivation:
    # x = r * step + base
    # r = (x - base) / step
    # ceil(r) = ceil((x - base) / step) = -((x - base) // -step)
    #     (ceil(a/b) = -(a // -b) -- https://stackoverflow.com/a/17511341)
    # ceil(r) * step + base = -((x - base) // -step) * step + base
    # #
    return -((x - base) // -step) * step + base

# endregion


BoundType: TypeAlias = Literal['()', '(]', '[)', '[]']
"""All possible ways to specify lower and upper bound inclusivities in the standard lusbir constructor.

'()' -> both bounds exclusive
'(]' -> exclusive lower bound, inclusive upper bound
'[)' -> inclusive lower bound, exclusive upper bound; the default choice
'[]' -> both bounds inclusive
"""

_bound_type_to_inclusivities = {
    '()': (False, False),
    '(]': (False, True),
    '[)': (True, False),
    '[]': (True, True),
}
_inclusivities_to_bound_type = {incl: bt for bt, incl in _bound_type_to_inclusivities.items()}


@final  # no guarantees that subclassing will work correctly
class Lusbir(Sequence):
    """An integer range characterized by a lower bound (lbound), upper bound (ubound), step, and base.

    The lower and upper bounds consist of an integer numeric bound and an inclusivity.
    The step and base are integers, and the step is nonzero.

    A number x is in the lusbir if and only if:
    - (numeric lower bound) <= x if the lower bound is inclusive;
      (numeric lower bound) <  x if the lower bound is exclusive
    - x <= (numeric upper bound) if the upper bound is inclusive;
      x <  (numeric upper bound) if the upper bound is exclusive
    - x is of the form (n * step + base) for some integer n

    Every number in the lusbir appears only once.
    Like Python ranges, lusbirs with a positive step are ordered from low to high
    and lusbirs with a negative step are ordered from high to low.

    Example: a lusbir with inclusive lower bound 0, exclusive upper bound 10, step 2, and base 1
    represents the list of all numbers x such that 0 <= x < 10 and x is of the form 2n + 1 for some integer n --
    or the list [1, 3, 5, 7, 9]. (Since the step is positive, the list is in ascending order.)

    Example: a lusbir with exclusive lower bound 5, inclusive upper bound 55, step -10, and base 5
    represents the list of all numbers x such that 5 < x <= 55 and x is of the form -10n + 5 for some integer n --
    or the list [55, 45, 35, 25, 15]. (Since the step is negative, the list is in descending order.)

    (See the __init__ docstring for details on the standard constructor.)
    """

    __slots__ = ['_range', '_lusb_tuple']

    _range: range
    _lusb_tuple: LusbTuple

    # region constructors

    @overload
    def __init__(self, ub_num: int, /): pass

    @overload
    def __init__(self, lb_num: int, ub_num: int, step: int = 1, base: int = 0, /): pass

    @overload
    def __init__(self, bound_type: BoundType, lb_num: int, ub_num: int, step: int = 1, base: int = 0, /): pass

    def __init__(self, /, *args):
        """Initialize this lusbir.

        Parameters (see "Calling options" for how to specify them):
            bound_type (str) - Specifies the inclusivities of the lower and upper bounds. One of the following options:
                '()' -> both bounds exclusive
                '(]' -> exclusive lower bound, inclusive upper bound
                '[)' (default if not specified) -> inclusive lower bound, exclusive upper bound
                '[]' -> both bounds inclusive
            lb_num (int) - Numeric lower bound. Defaults to 0 if not specified.
            ub_num (int) - Numeric upper bound. Must always be specified.
            step (int) - Must be nonzero. Defaults to 1 if not specified.
            base (int) - Defaults to 0 if not specified.

        Calling options (distinguished by the number and types of arguments):
            Lusbir(ub_num)
            Lusbir(lb_num, ub_num[, step[, base]])
            Lusbir(bound_type, lb_num, ub_num[, step[, base]])

        If the step is 0, or the bound type is not one of the outlined options, raise a ValueError.


        >>> list(Lusbir(10))
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> list(Lusbir(10, 20))
        [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        >>> list(Lusbir(10, 20, 2))
        [10, 12, 14, 16, 18]
        >>> list(Lusbir(10, 20, 2, 1))
        [11, 13, 15, 17, 19]
        >>> list(Lusbir('()', 0, 10))
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> list(Lusbir('(]', 0, 10))
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> list(Lusbir('[)', 0, 10))
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> list(Lusbir('[]', 0, 10))
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> list(Lusbir('(]', 0, 10, 2))
        [2, 4, 6, 8, 10]
        >>> list(Lusbir('(]', 0, 10, 2, 1))
        [1, 3, 5, 7, 9]


        >>> list(Lusbir(-20, -10))
        [-20, -19, -18, -17, -16, -15, -14, -13, -12, -11]
        >>> list(Lusbir('(]', -20, -10))
        [-19, -18, -17, -16, -15, -14, -13, -12, -11, -10]

        >>> list(Lusbir(0, 30, 3, 2))
        [2, 5, 8, 11, 14, 17, 20, 23, 26, 29]
        >>> list(Lusbir(0, 30, -3, 2))  # negating the step always reverses the represented list
        [29, 26, 23, 20, 17, 14, 11, 8, 5, 2]

        >>> list(Lusbir(-50, 50, 10, 9))
        [-41, -31, -21, -11, -1, 9, 19, 29, 39, 49]
        >>> list(Lusbir(-50, 50, 10, 1009))  # adding a multiple of the step to the base does not change anything
        [-41, -31, -21, -11, -1, 9, 19, 29, 39, 49]
        >>> list(Lusbir(-50, 50, 10, -1))
        [-41, -31, -21, -11, -1, 9, 19, 29, 39, 49]


        While Python ranges are based on a start value and a stop bound, lusbirs are based on lower and upper bounds.

        >>> list(range(10, 0, -1))
        [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        >>> list(Lusbir(10, 0, -1))  # bounds: 10 <= x < 0 -- never satisfied
        []
        >>> list(Lusbir(0, 10, -1))  # bounds: 0 <= x < 10, or 10 > x >= 0
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        >>> list(Lusbir('(]', 0, 10, -1))  # bounds: 0 < x <= 10, or 10 >= x > 0
        [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

        >>> list(range(5, 55, 10))  # 10n + 5 because the step is 10 and the start value is 5
        [5, 15, 25, 35, 45]
        >>> list(Lusbir(5, 55, 10))  # 10n + 0 because the step is 10 and the base is, by default, 0
        [10, 20, 30, 40, 50]
        >>> list(Lusbir(5, 55, 10, 5))
        [5, 15, 25, 35, 45]
        >>> list(Lusbir('(]', 5, 55, 10, 5))
        [15, 25, 35, 45, 55]
        >>> list(Lusbir('(]', 5, 55, -10, 5))
        [55, 45, 35, 25, 15]
        """

        match args:
            case [int(ub_num)]:
                lb_num = 0
                lb_incl = True
                ub_incl = False
                other_args = []
            case [int(lb_num), int(ub_num), *other_args]:
                lb_incl = True
                ub_incl = False
            case [str(bound_type), int(lb_num), int(ub_num), *other_args]:
                try:
                    lb_incl, ub_incl = _bound_type_to_inclusivities[bound_type]
                except KeyError:
                    raise ValueError(f'invalid lusbir bound type: {repr(bound_type)}') from None
            case _:
                raise Lusbir._invalid_arguments_error(args)

        match other_args:
            case []:
                step = 1
                base = 0
            case [int(step)]:
                base = 0
            case [int(step), int(base)]:
                pass
            case _:
                raise Lusbir._invalid_arguments_error(args)

        self._init_from_lusb_tuple(LusbTuple(Bound(lb_num, lb_incl), Bound(ub_num, ub_incl), step, base))

    @staticmethod
    def _invalid_arguments_error(args: tuple, /) -> TypeError:
        arg_types = tuple(type(arg).__name__ for arg in args)
        return TypeError(f'invalid lusbir arguments -- argument types received were: {arg_types}')

    @classmethod
    def from_lusb_tuple(cls, lusb_tuple: LusbTuple, /) -> 'Lusbir':
        """Alternative constructor. Construct the lusbir from a lusb tuple.

        Raise a ValueError if the lusb tuple has a step of 0.
        """
        lusbir = object.__new__(cls)
        lusbir._init_from_lusb_tuple(lusb_tuple)
        return lusbir

    def _init_from_lusb_tuple(self, lusb_tuple: LusbTuple, /) -> None:
        if lusb_tuple.step == 0:
            raise ValueError('lusbir step cannot be 0')
        self._range = _lusb_tuple_to_range(lusb_tuple)
        self._lusb_tuple = lusb_tuple

    # endregion

    # region original functionality

    @property
    def lbound(self, /) -> Bound:
        """The lower bound of this lusbir. A named tuple `Bound(number: int, inclusive: bool)`."""
        return self._lusb_tuple.lbound

    @property
    def ubound(self, /) -> Bound:
        """The upper bound of this lusbir. A named tuple `Bound(number: int, inclusive: bool)`."""
        return self._lusb_tuple.ubound

    @property
    def step(self, /) -> int:
        """The step of this lusbir. A nonzero integer."""
        return self._lusb_tuple.step

    @property
    def base(self, /) -> int:
        """The base of this lusbir. An integer."""
        return self._lusb_tuple.base

    @property
    def lusb_tuple(self, /) -> LusbTuple:
        """The four pieces of information that characterize this lusbir, in the form of a lusb tuple."""
        return self._lusb_tuple

    def __eq__(self, other, /) -> bool:
        """If `other` is a lusbir, return whether it represents the same list as this lusbir."""
        if isinstance(other, Lusbir):
            return self._range == other._range
        return NotImplemented

    @overload
    def __getitem__(self, index: int, /) -> int: pass

    @overload
    def __getitem__(self, slice_: slice, /) -> 'Lusbir': pass

    def __getitem__(self, subscript, /):
        """Return self[subscript], according to standard indexing and slicing conventions for sequences.

        The return value is an integer when indexing and another lusbir when slicing.
        """
        if isinstance(subscript, int):
            try:
                return self._range[subscript]
            except IndexError:
                raise IndexError(f'lusbir index out of range: {subscript}') from None
        if isinstance(subscript, slice):
            return Lusbir.from_range(self._range[subscript])
        raise TypeError(f'lusbir subscripts must be integers or slices, not {repr(type(subscript).__name__)}')

    def __hash__(self, /) -> int:
        """Return an appropriate hash for this lusbir.

        Two lusbirs that represent the same list will always hash to the same value,
        even if they have different lusb tuples.
        """
        # Just return the hash of the underlying Python range --
        # lusbirs and Python ranges probably won't be used in the same places in code anyway.
        return hash(self._range)

    def __iter__(self, /) -> Iterator[int]:
        """Return an iterator such that `list(self)` evaluates to the list represented by this lusbir."""
        return iter(self._range)

    def __repr__(self, /) -> str:
        """Return a string s such that eval(s).lusb_tuple == self.lusb_tuple."""
        # Format: `Lusbir(bound_type, lb_num, ub_num[, step[, base]])`;
        # `step` and `base` are only included if they are different from their default values.
        (lb_num, lb_incl), (ub_num, ub_incl), step, base = self._lusb_tuple
        bound_type = _inclusivities_to_bound_type[lb_incl, ub_incl]
        if base != 0:
            return f'Lusbir({repr(bound_type)}, {lb_num}, {ub_num}, {step}, {base})'
        elif step != 1:
            return f'Lusbir({repr(bound_type)}, {lb_num}, {ub_num}, {step})'
        else:
            return f'Lusbir({repr(bound_type)}, {lb_num}, {ub_num})'

    @staticmethod
    def from_range(r: range, /) -> 'Lusbir':
        """Return a lusbir that represents the same list as the given Python range."""
        if r.step > 0:
            return Lusbir('[)', r.start, r.stop, r.step, r.start)
        else:
            return Lusbir('(]', r.stop, r.start, r.step, r.start)

    def to_range(self, /) -> range:
        """Return a Python range that represents the same list as this lusbir."""
        return self._range

    # endregion

    # region functionality from `range`

    def __bool__(self, /) -> bool:
        """Return len(self) > 0."""
        return bool(self._range)

    def __contains__(self, x: int, /) -> bool:
        """Return x in self."""
        return x in self._range

    def __len__(self, /) -> int:
        """Return len(self)."""
        return len(self._range)

    def __reversed__(self, /) -> Iterator[int]:
        """Return a reverse iterator."""
        return reversed(self._range)

    def count(self, x: int, /) -> int:
        """Return the number of occurrences of x."""
        return self._range.count(x)

    def index(self, x: int, /) -> int:  # noqa
        """Return the index of x.

        Raise ValueError if x is not present.
        """
        try:
            return self._range.index(x)
        except ValueError:
            raise ValueError(f'lusbir does not contain {repr(x)}') from None

    # endregion
