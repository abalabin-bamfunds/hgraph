import pytest

from typing import cast, Type

from hg import TIME_SERIES_TYPE, compute_node, REF, TS, TSL, Size, SIZE, graph
from hg._types._ref_type import TimeSeriesReference
from hg._types._type_meta_data import AUTO_RESOLVE
from hg.test import eval_node


@compute_node
def create_ref(ts: REF[TIME_SERIES_TYPE]) -> REF[TIME_SERIES_TYPE]:
    return ts.value


def test_ref():
    assert eval_node(create_ref[TIME_SERIES_TYPE: TS[int]], ts=[1, 2]) == [1, 2]


@compute_node
def route_ref(condition: TS[bool], ts: REF[TIME_SERIES_TYPE]) -> TSL[REF[TIME_SERIES_TYPE], Size[2]]:
    return cast(TSL, (ts.value, TimeSeriesReference()) if condition.value else (TimeSeriesReference(), ts.value))


@pytest.mark.xfail(reason="Not implemented", strict=True)
def test_route_ref():
    assert eval_node(route_ref[TIME_SERIES_TYPE: TS[int]], condition=[True, None, False, None], ts=[1, 2, None, 4]) == [
        {0: 1}, {0: 2}, {1: 2}, {1: 4}]


@compute_node
def merge_ref(index: TS[int], ts: TSL[REF[TIME_SERIES_TYPE], SIZE]) -> REF[TIME_SERIES_TYPE]:
    return cast(REF, ts[index.value].value)


def test_merge_ref():
    assert eval_node(merge_ref[TIME_SERIES_TYPE: TS[int], SIZE: Size[2]], index=[0, None, 1, None], ts=[(1, -1), (2, -2), None, (4, -4)]) == [1, 2, -2, -4]


@graph
def merge_ref_non_peer(index: TS[int], ts1: TIME_SERIES_TYPE, ts2: TIME_SERIES_TYPE, tp: Type[TIME_SERIES_TYPE] = AUTO_RESOLVE) -> REF[TIME_SERIES_TYPE]:
    return merge_ref(index, TSL[tp, Size[2]].from_ts(ts1, ts2))  # TODO: This TSL building syntax is quite a mouthful, TSL(ts1, ts2) would be preferrable, ideally wiring should accept just (ts1, ts2) here


def test_merge_ref_non_peer():
    assert eval_node(merge_ref_non_peer[TIME_SERIES_TYPE: TS[int]],
                     index=[0, None, 1, None],
                     ts1=[1, 2, None, 4],
                     ts2=[-1, -2, None, -4]
                     ) == [1, 2, -2, -4]