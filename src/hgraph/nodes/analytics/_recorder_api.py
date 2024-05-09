from abc import abstractmethod
from datetime import datetime, date
from typing import Sequence, Any, Generic

from hgraph import COMPOUND_SCALAR, Frame, GlobalState

__all__ = ("RecorderAPI", "TableAPI", "TableReaderAPI", "TableWriterAPI", "register_recorder_api")


def register_recorder_api(recorder: "RecorderAPI"):
    """
    Register a recorder API instance with the global state.
    This should be done just before running a graph that requires this functionality, preferably within a
    with GlobalState() context. For example:

    with GlobalState():
        register_recorder_api(MyTableAPI())
        evaluate_graph(my_graph, config)

    """
    GlobalState.instance().__recorder_api__ = recorder


def get_recorder_api() -> "RecorderAPI":
    """
    Decorator that registers a recorder API as a global state.
    """
    return GlobalState.instance().__recorder_api__


class RecorderAPI:

    @abstractmethod
    def has_table_definition(self, table_name: str) -> bool:
        """Is there a table definition for this table_name?"""

    @abstractmethod
    def create_or_update_table_definition(self, table_name: str, definition: type[COMPOUND_SCALAR],
                                          date_column: tuple[str, date | datetime],
                                          renamed_fields: dict[str, str] = None) -> None:
        """
        Defines a table definition for a table. This is used for validation and can perform operations such
        as creating a database tables etc. If we are re-defining a table, then any new columns should have a default
        value provided to initialise the column value.
        If columns are missing, it is assumed that the column is dropped, unless the column is present in the
        renamed_fields dictionary. There is currently no support for re-defining the types of columns.
        If that is needed, a custom conversion script should be created to read-write-rename the tables.
        """

    @abstractmethod
    def rename_table_definition(self, table_name: str, new_table_name: str):
        """
        Renames a table definition. This is useful when re-factoring a table.
        """

    @abstractmethod
    def drop_table(self, table_name: str):
        """
        Removes a table and its definition.
        """

    @abstractmethod
    def reset_table(self):
        """
        Removes all the data associated to a table.
        """

    @abstractmethod
    def get_table_writer(self, table_name: str, variant: str = None):
        """
        A writer instance for the given table name.
        The writer will support writing data to the table, it will track the current engine time under the covers.
        When using the graph engine time, this code must be executed within the confines of the graph evaluation thread.
        The date column is not exposed directly to the table writer, and the writer does not write the date; this
        is picked up from the underlying engine time.

        The table can be used with a variant label, this allows for different recordings using the same schema,
        but keeping the results isolated.
        """

    @abstractmethod
    def get_table_reader(self, table_name: str, variant: str = None):
        """
        A reader instance for the given table name.
        The table reader strips out the date column and returns the subset of data associated to the date.
        The date/datetime is loaded from the underlying engine time.

        The variant allows for different independent runs to be used, whilst maintaining the same data description.
        """


class TableAPI(Generic[COMPOUND_SCALAR]):
    """
    All table API implementations provide basic information describing the table
    """

    @property
    @abstractmethod
    def as_of_time(self) -> datetime:
        """
        The time to use to consider when to view the data set from. The time which we consider the data to be
        available from. For example, the data we are using was produced on t1, but at t2 new data arrived that
        back-filled results, so when we re-run, the data will be different. Using as_of allows us to see
        how the data appeared at that point in time rather than the current data.
        """

    @property
    @abstractmethod
    def current_time(self) -> datetime:
        """The current time for this engine cycle"""

    @current_time.setter
    @abstractmethod
    def current_time(self, value: datetime):
        """
        Set the time, when recording this will add the next row using the data from current_time,
        when replaying the data will be loaded using this time.
        """

    @property
    @abstractmethod
    def date_column(self) -> tuple[str, type[date | datetime]]:
        """The date column and type of the date column"""

    @property
    @abstractmethod
    def schema(self) -> COMPOUND_SCALAR:
        """The schema defining the shape of this table. (Not including the date field)"""


class TableWriterAPI(TableAPI[COMPOUND_SCALAR], Generic[COMPOUND_SCALAR]):

    @abstractmethod
    def write_columns(self, **kwargs):
        """
        Use this to write simple values that translate to a single row for this engine cycle
        """
        ...

    @abstractmethod
    def write_rows(self, rows: Sequence[tuple[Any, ...] | dict[str, Any]]):
        """
        Use this to write a collection of rows to the table.
        When rows need to be written, the table must be fully populated.
        """
        ...

    @abstractmethod
    def flush(self):
        """Flush the state to the underlying store"""


class TableReaderAPI(TableAPI[COMPOUND_SCALAR], Generic[COMPOUND_SCALAR]):

    @abstractmethod
    def get_frame(self) -> Frame[COMPOUND_SCALAR]:
        """Returns the frame of data associated to the current date"""

    @abstractmethod
    def get_next_available_time(self) -> datetime | None:
        """
        The next available time present in recorded data set. If there is no next available time, None is returned.
        """
