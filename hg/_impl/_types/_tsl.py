from datetime import datetime
from typing import Generic, Optional, Any

from frozendict import frozendict

from hg._impl._types._input import PythonBoundTimeSeriesInput
from hg._impl._types._output import PythonTimeSeriesOutput
from hg._types._scalar_types import SIZE
from hg._types._time_series_types import TimeSeriesOutput, TimeSeriesInput, TIME_SERIES_TYPE
from hg._types._tsl_type import TimeSeriesListInput, TimeSeriesListOutput

__all__ = ("PythonTimeSeriesListOutput", "PythonTimeSeriesListInput")


class PythonTimeSeriesListOutput(PythonTimeSeriesOutput, TimeSeriesListOutput[TIME_SERIES_TYPE, SIZE],
                                 Generic[TIME_SERIES_TYPE, SIZE]):

    def __init__(self, __type__: TIME_SERIES_TYPE, __size__: SIZE, *args, **kwargs):
        Generic.__init__(self)
        TimeSeriesListInput.__init__(self, __type__, __size__)
        PythonTimeSeriesOutput.__init__(self, *args, **kwargs)

    def value(self) -> Optional[tuple]:
        return tuple(ts.value if ts.valid else None for ts in self._ts_values)

    @property
    def delta_value(self) -> Optional[dict[int, Any]]:
        return {i: ts.delta_value for i, ts in enumerate(self._ts_values) if ts.modified}

    def apply_result(self, result: Any):
        if result is None:
            return
        if isinstance(result, (dict, frozendict)):
            for k, v in result.items():
                self[k].apply_result(v)
        elif isinstance(result, (tuple, list)):
            if len(result) != len(self._ts_values):
                raise ValueError(f"Expected {len(self._ts_values)} elements, got {len(result)}")
            for ts, value in zip(self._ts_values, result):
                ts.apply_result(value)

    def copy_from_output(self, output: "TimeSeriesOutput"):
        for ts_self, ts_output in zip(self.values(), output.values()):
            ts_self.copy_from_output(ts_output)

    def copy_from_input(self, input: "TimeSeriesInput"):
        for ts_self, ts_input in zip(self.values(), input.values()):
            ts_self.copy_from_input(ts_input)

    def mark_invalid(self):
        if self.valid:
            for v in self.values():
                v.mark_invalid()
            super().mark_invalid()

    @property
    def all_valid(self) -> bool:
        return all(ts.valid for ts in self.values())


class PythonTimeSeriesListInput(PythonBoundTimeSeriesInput, TimeSeriesListInput[TIME_SERIES_TYPE, SIZE],
                                Generic[TIME_SERIES_TYPE, SIZE]):

    def __init__(self, __type__: TIME_SERIES_TYPE, __size__: SIZE, _owning_node: "Node" = None,
                 _parent_input: "TimeSeriesInput" = None):
        Generic.__init__(self)
        TimeSeriesListInput.__init__(self, __type__, __size__)
        PythonBoundTimeSeriesInput.__init__(self, _owning_node=_owning_node, _parent_input=_parent_input)

    @property
    def has_peer(self) -> bool:
        return super().bound

    @property
    def bound(self) -> bool:
        return super().bound or any(ts.bound for ts in self.values())

    def bind_output(self, output: TimeSeriesOutput):
        output: PythonTimeSeriesListOutput
        super().bind_output(output)
        for ts_input, ts_output in zip(self.values(), output.values()):
            ts_input.bind_output(ts_output)

    @property
    def active(self) -> bool:
        """
        For UnBound TS, if any of the elements are active we report the input as active,
        Note, that make active / make passive will make ALL instances active / passive.
        Thus, just because the input returns True for active, it does not mean that make_active is a no-op.
        """
        if self.has_peer:
            return super().active
        else:
            return any(ts.active for ts in self.values())

    def make_active(self):
        if self.has_peer:
            super().make_active()
        else:
            for ts in self.values():
                ts.make_active()

    def make_passive(self):
        if self.has_peer:
            super().make_passive()
        else:
            for ts in self.values():
                ts.make_passive()

    @property
    def value(self):
        if self.has_peer:
            return super().value
        else:
            return tuple(ts.value if ts.valid else None for ts in self.values())

    @property
    def delta_value(self):
        if self.has_peer:
            return super().delta_value
        else:
            return {k: ts.delta_value for k, ts in self.modified_items()}

    @property
    def modified(self) -> bool:
        if self.has_peer:
            return super().modified
        else:
            return any(ts.modified for ts in self.values())

    @property
    def valid(self) -> bool:
        if self.has_peer:
            return super().valid
        else:
            return any(ts.valid for ts in self.values())

    @property
    def all_valid(self) -> bool:
        return all(ts.valid for ts in self.values())

    @property
    def last_modified_time(self) -> datetime:
        if self.has_peer:
            return super().last_modified_time
        else:
            return max(ts.last_modified_time for ts in self.values())

