# To test:
#     - Baseline constructor
#         - For lusb tuples lt with nonzero step, Lusbir.from_lusb_tuple(lt).lusb_tuple == lt
#         - For lusb tuples with a step of 0, `from_lusb_tuple` raises a ValueError
#     - Fundamental correctness: a lusbir corresponds to the appropriate list for its lusb tuple
#         - Inclusion: a number is in the lusbir iff it is between the lower and upper bounds and is of the form
#               n * step + base, n integer
#         - Uniqueness: lusbirs do not contain duplicate elements
#         - Order: lusbirs with positive step are in ascending order
#           and lusbirs with negative step are in descending order
#     - Standard constructor
#         - All valid calls to `__init__` produce a lusbir that has the same lusb tuple
#           as a lusbir produced by the appropriate call to `from_lusb_tuple`
#         - A ValueError is raised whenever a step of 0 is provided
#     - Properties
#         - lbound, ubound, step, and base correspond to the appropriate properties on the lusbir's lusb tuple
#     - Range conversions
#         - For any lusbir lr, list(lr.to_range()) == list(lr)
#         - For any range r, list(Lusbir.from_range(r)) == list(r)
#     - Misc functionality
#         - For any lusbir lr and slice s, lr[s] is a lusbir and list(lr[s]) == list(lr.to_range()[s])
#         - Lusbirs compare equal iff they represent the same list
#         - If lusbirs compare equal, then they have the same hash
#         - For any lusbir lr, eval(repr(lr)).lusb_tuple == lr.lusb_tuple
#         - For any lusbir lr, list(reversed(lr)) == list(reversed(lr.to_range()))
#     - `range`-matching functionality: <lusbir>.<function>(<args>) and <lusbir>.to_range().<function>(<args>)
#       either both give the same output or both raise the same type of error
#         - __getitem__ for integer subscripts
#         - __bool__
#         - __contains__
#         - __len__
#         - count
#         - index
#
# Coverage:
#     Bound, LusbTuple, BoundType: not explicitly tested
#     __init__: Standard constructor; calls with invalid arguments / invalid bound types are left untested here
#     from_lusb_tuple: Baseline constructor
#     lbound, ubound, step, base: Properties
#     lusb_tuple: canonical source of truth for the lusb tuple of a given lusbir
#     __eq__: Misc functionality; only same-type comparisons are tested here
#     __getitem__: Misc functionality (slicing) and `range`-matching functionality (indexing)
#     __hash__: Misc functionality
#     __iter__: canonical source of truth for the list represented by a given lusbir
#     __repr__: Misc functionality
#     from_range: Range conversions
#     to_range: Range conversions
#     __bool__: `range`-matching functionality
#     __contains__: `range`-matching functionality
#     __len__: `range`-matching functionality
#     __reversed__: Misc functionality
#     count: `range`-matching functionality
#     index: `range`-matching functionality
# #

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis.strategies import booleans, builds, composite, integers, sampled_from, slices
from pytest import raises

from lusbir import Bound, LusbTuple, Lusbir


@given(integers(), booleans(), integers(), booleans(), integers(), integers())
def test_baseline_constructor(lb_num, lb_incl, ub_num, ub_incl, step, base):
    lt = LusbTuple(Bound(lb_num, lb_incl), Bound(ub_num, ub_incl), step, base)
    if step == 0:
        with raises(ValueError):
            Lusbir.from_lusb_tuple(lt)
    else:
        assert Lusbir.from_lusb_tuple(lt).lusb_tuple == lt


MAX_INT_SIZE = 1000


def integers_within_size():
    return integers(min_value=-MAX_INT_SIZE, max_value=MAX_INT_SIZE)


def nonzero_integers_within_size():
    return integers_within_size().filter(lambda x: x != 0)


@composite
def lusbirs(draw):
    lb_num = draw(integers_within_size())
    lb_incl = draw(booleans())
    ub_num = draw(integers_within_size())
    ub_incl = draw(booleans())
    step = draw(nonzero_integers_within_size())
    base = draw(integers_within_size())
    return Lusbir.from_lusb_tuple(LusbTuple(Bound(lb_num, lb_incl), Bound(ub_num, ub_incl), step, base))


def contains(lusbir: Lusbir, x: int) -> bool:
    (lb_num, lb_incl), (ub_num, ub_incl), step, base = lusbir.lusb_tuple
    within_lower_bound = lb_num <= x if lb_incl else lb_num < x
    within_upper_bound = x <= ub_num if ub_incl else x < ub_num
    congruent_to_base_modulo_step = (x - base) % step == 0
    return within_lower_bound and within_upper_bound and congruent_to_base_modulo_step


@given(lusbirs(), integers())
def test_inclusion_correctness(lusbir, x):
    assert (x in list(lusbir)) == contains(lusbir, x)


@given(lusbirs())
def test_uniqueness_correctness(lusbir):
    assert len(list(lusbir)) == len(set(lusbir))


@given(lusbirs())
def test_order_correctness(lusbir):
    assert list(lusbir) == sorted(list(lusbir), reverse=lusbir.lusb_tuple.step < 0)


bound_type_to_inclusivities = {
    '()': (False, False),
    '(]': (False, True),
    '[)': (True, False),
    '[]': (True, True),
}
bound_types = list(bound_type_to_inclusivities)


@given(sampled_from(bound_types), integers(), integers(), integers(), integers())
def test_standard_constructor(bound_type, lb_num, ub_num, step, base):
    lb_incl, ub_incl = bound_type_to_inclusivities[bound_type]
    constructor_args_to_lusb_tuple_args = {
        (ub_num,): ((0, True), (ub_num, False), 1, 0),
        (lb_num, ub_num): ((lb_num, True), (ub_num, False), 1, 0),
        (lb_num, ub_num, step): ((lb_num, True), (ub_num, False), step, 0),
        (lb_num, ub_num, step, base): ((lb_num, True), (ub_num, False), step, base),
        (bound_type, lb_num, ub_num): ((lb_num, lb_incl), (ub_num, ub_incl), 1, 0),
        (bound_type, lb_num, ub_num, step): ((lb_num, lb_incl), (ub_num, ub_incl), step, 0),
        (bound_type, lb_num, ub_num, step, base): ((lb_num, lb_incl), (ub_num, ub_incl), step, base),
    }
    for constructor_args, ((l_n, l_i), (u_n, u_i), s, b) in constructor_args_to_lusb_tuple_args.items():
        lusb_tuple = LusbTuple(Bound(l_n, l_i), Bound(u_n, u_i), s, b)
        if lusb_tuple.step == 0:
            with pytest.raises(ValueError):
                Lusbir(*constructor_args)  # noqa
        else:
            assert Lusbir(*constructor_args).lusb_tuple == lusb_tuple  # noqa


@given(lusbirs())
def test_properties(lusbir):
    assert (lusbir.lbound, lusbir.ubound, lusbir.step, lusbir.base) == lusbir.lusb_tuple


@given(lusbirs())
def test_to_range(lusbir):
    assert list(lusbir.to_range()) == list(lusbir)


def ranges():
    return builds(range, integers_within_size(), integers_within_size(), nonzero_integers_within_size())


@given(ranges())
def test_from_range(r):
    assert list(Lusbir.from_range(r)) == list(r)


@given(lusbirs(), slices(MAX_INT_SIZE))  # noqa
def test_slicing(lusbir, s):
    assert isinstance(lusbir[s], Lusbir)
    assert list(lusbir[s]) == list(lusbir.to_range()[s])


@given(lusbirs(), lusbirs())
def test_equality(lusbir_0, lusbir_1):
    assert (lusbir_0 == lusbir_1) == (list(lusbir_0) == list(lusbir_1))


@given(lusbirs(), lusbirs())
def test_hashing(lusbir_0, lusbir_1):
    assume(lusbir_0 == lusbir_1)
    assert hash(lusbir_0) == hash(lusbir_1)


@given(lusbirs())
def test_repr(lusbir):
    assert eval(repr(lusbir)).lusb_tuple == lusbir.lusb_tuple


@given(lusbirs())
def test_reversed(lusbir):
    assert list(reversed(lusbir)) == list(reversed(lusbir.to_range()))


@dataclass
class Output:
    value: Any


@dataclass
class Error:
    type: type


def try_call(f: Callable, *args, **kwargs) -> Output | Error:
    try:
        return Output(f(*args, **kwargs))
    except Exception as e:
        return Error(type(e))


@given(lusbirs(), integers())
def test_range_matching_functionality(lusbir, x):
    funcs = [
        lambda c: c[x],
        lambda c: bool(c),
        lambda c: x in c,
        lambda c: len(c),
        lambda c: c.count(x),
        lambda c: c.index(x),
    ]
    for func in funcs:
        assert try_call(func, lusbir) == try_call(func, lusbir.to_range())
