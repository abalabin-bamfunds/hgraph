from typing import Type, TypeVar, Optional, _GenericAlias

__all__ = (
    "HgTSWTypeMetaData",
    "HgTSWOutTypeMetaData",
)

from hgraph._types._generic_rank_util import scale_rank
from hgraph._types._ts_type_var_meta_data import HgTsTypeVarTypeMetaData
from hgraph._types._type_meta_data import ParseError
from hgraph._types._scalar_type_meta_data import HgScalarTypeMetaData
from hgraph._types._tsb_meta_data import HgTimeSeriesTypeMetaData

__all__ = ("HgTSWTypeMetaData", "HgTSWOutTypeMetaData")


class HgTSWTypeMetaData(HgTimeSeriesTypeMetaData):
    """Parses TSW[...]"""

    value_scalar_tp: HgScalarTypeMetaData
    size_tp: HgScalarTypeMetaData
    min_size_tp: HgScalarTypeMetaData

    def __init__(
        self, scalar_type: HgScalarTypeMetaData, size_tp: HgScalarTypeMetaData, min_size_tp: HgScalarTypeMetaData
    ):
        self.value_scalar_tp = scalar_type
        self.size_tp = size_tp
        self.min_size_tp = min_size_tp

    @property
    def is_resolved(self) -> bool:
        return self.value_scalar_tp.is_resolved and self.size_tp.is_resolved and self.min_size_tp.is_resolved

    @property
    def type_vars(self):
        return self.value_scalar_tp.type_vars | self.size_tp.type_vars | self.min_size_tp.type_vars

    @property
    def generic_rank(self) -> dict[type, float]:
        return scale_rank(self.value_scalar_tp.generic_rank, 0.01)

    @property
    def py_type(self) -> Type:
        from hgraph._types._ts_type import TS

        return TS[self.value_scalar_tp.py_type]

    def resolve(self, resolution_dict: dict[TypeVar, "HgTypeMetaData"], weak=False) -> "HgTypeMetaData":
        if self.is_resolved:
            return self
        else:
            return type(self)(
                self.value_scalar_tp.resolve(resolution_dict, weak),
                self.size_tp.resolve(resolution_dict, weak),
                self.min_size_tp.resolve(resolution_dict, weak),
            )

    def do_build_resolution_dict(self, resolution_dict: dict[TypeVar, "HgTypeMetaData"], wired_type: "HgTypeMetaData"):
        super().do_build_resolution_dict(resolution_dict, wired_type)
        wired_type: HgTSWTypeMetaData
        self.value_scalar_tp.build_resolution_dict(resolution_dict, wired_type.value_scalar_tp if wired_type else None)
        self.size_tp.build_resolution_dict(resolution_dict, wired_type.size_tp if wired_type else None)
        self.min_size_tp.build_resolution_dict(resolution_dict, wired_type.min_size_tp if wired_type else None)

    def build_resolution_dict_from_scalar(
        self, resolution_dict: dict[TypeVar, "HgTypeMetaData"], wired_type: "HgTypeMetaData", value: object
    ):
        self.value_scalar_tp.build_resolution_dict(resolution_dict, wired_type)

    def scalar_type(self) -> "HgScalarTypeMetaData":
        return self.value_scalar_tp

    @classmethod
    def parse_type(cls, value_tp) -> Optional["HgTypeMetaData"]:
        from hgraph._types._tsw_type import TimeSeriesWindowInput

        if isinstance(value_tp, _GenericAlias) and value_tp.__origin__ is TimeSeriesWindowInput:
            scalar = HgScalarTypeMetaData.parse_type(value_tp.__args__[0])
            size = HgScalarTypeMetaData.parse_type(value_tp.__args__[1])
            min_size = HgScalarTypeMetaData.parse_type(value_tp.__args__[2])
            if scalar is None:
                raise ParseError(
                    f"While parsing 'TSW[{str(value_tp.__args__[0])}, "
                    f"{str(value_tp.__args__[1])}, "
                    f"{str(value_tp.__args__[2])}]' unable to parse scalar type from"
                    f" '{str(value_tp.__args__[0])}'"
                )
            if size is None:
                raise ParseError(
                    f"While parsing 'TSW[{str(value_tp.__args__[0])}, "
                    f"{str(value_tp.__args__[1])}, "
                    f"{str(value_tp.__args__[2])}]' unable to parse size type from"
                    f" '{str(value_tp.__args__[1])}'"
                )
            if min_size is None:
                raise ParseError(
                    f"While parsing 'TSW[{str(value_tp.__args__[0])}, "
                    f"{str(value_tp.__args__[1])}, "
                    f"{str(value_tp.__args__[2])}]' unable to parse min_size type from"
                    f" '{str(value_tp.__args__[2])}'"
                )
            return HgTSWTypeMetaData(scalar, size, min_size)

    def matches(self, tp: "HgTypeMetaData") -> bool:
        # TODO: If we loose the TS_OUT type we can return to an is, which is much faster.
        return (
            issubclass((tp_ := type(tp)), HgTSWTypeMetaData) and self.value_scalar_tp.matches(tp.value_scalar_tp)
        ) or tp_ in (HgTimeSeriesTypeMetaData, HgTsTypeVarTypeMetaData)

    def __eq__(self, o: object) -> bool:
        return (
            type(o) is HgTSWTypeMetaData
            and self.value_scalar_tp == o.value_scalar_tp
            and self.size_tp == o.size_tp
            and self.min_size_tp == o.min_size_tp
        )

    def __str__(self) -> str:
        return f"TSW[{str(self.value_scalar_tp)}]"

    def __repr__(self) -> str:
        return f"HgTSWTypeMetaData({repr(self.value_scalar_tp)}, {repr(self.size_tp)}, {repr(self.min_size_tp)})"

    def __hash__(self) -> int:
        from hgraph._types._tsw_type import TSW

        return hash(TSW) ^ hash(self.value_scalar_tp) ^ hash(self.size_tp) ^ hash(self.min_size_tp)


class HgTSWOutTypeMetaData(HgTSWTypeMetaData):
    """Parses TSW_OUT[...]"""

    @classmethod
    def parse_type(cls, value_tp) -> Optional["HgTypeMetaData"]:
        from hgraph._types._tsw_type import TimeSeriesWindowOutput

        if isinstance(value_tp, _GenericAlias) and value_tp.__origin__ is TimeSeriesWindowOutput:
            return HgTSWOutTypeMetaData(
                HgScalarTypeMetaData.parse_type(value_tp.__args__[0]),
                HgScalarTypeMetaData.parse_type(value_tp.__args__[1]),
                HgScalarTypeMetaData.parse_type(value_tp.__args__[2]),
            )

    def __eq__(self, o: object) -> bool:
        return (
            type(o) is HgTSWOutTypeMetaData
            and self.value_scalar_tp == o.value_scalar_tp
            and self.size_tp == o.size_tp
            and self.min_size_tp == o.min_size_tp
        )

    def __str__(self) -> str:
        return f"TSW_OUT[{str(self.value_scalar_tp)}]"

    def __repr__(self) -> str:
        return f"HgTSWOutTypeMetaData({repr(self.value_scalar_tp)}, {repr(self.size_tp)}, {repr(self.min_size_tp)})"

    def __hash__(self):
        return super().__hash__()
