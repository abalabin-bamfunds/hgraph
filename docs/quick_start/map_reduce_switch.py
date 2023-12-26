from hgraph import compute_node, TS, graph, TSD, map_, TSL, Size, sink_node, TIME_SERIES_TYPE, pass_through
from hgraph.test import eval_node

# Map
#
# @compute_node
# def convert(ts: TS[int]) -> TS[str]:
#     """Convert the input to a time series."""
#     return str(ts.value)
#
#
# @graph
# def graph_tsd(tsd: TSD[str, TS[int]]) -> TSD[str, TS[str]]:
#     return map_(convert, tsd)
#
#
# print(eval_node(graph_tsd, tsd=[{"a": 1, "b": 6}, {"a": 2, "b": 7}]))
#
#
# @graph
# def graph_tsl(tsl: TSL[TS[int], Size[2]]) -> TSL[TS[str], Size[2]]:
#     return map_(convert, tsl)
#
#
# print(eval_node(graph_tsl, tsl=[{0: 1, 1: 6}, {0: 2, 1: 7}]))


@sink_node
def print_input(key: TS[str], ts: TIME_SERIES_TYPE, mode: str):
    print(f"[{mode}] {key.value}: {ts.delta_value}")


@graph
def graph_undecided(tsd: TSD[str, TS[int]]):
    map_(print_input, tsd, "No Passthrough")
    map_(print_input, pass_through(tsd), "Passthrough", __keys__=tsd.key_set)


print(eval_node(graph_undecided, tsd=[{"a": 1, "b": 6}, {"a": 2, "b": 7}]))

# Reduce
