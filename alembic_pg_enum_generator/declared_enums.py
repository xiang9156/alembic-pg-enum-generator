from typing import Any, Callable, List, Optional, Tuple, Union

import sqlalchemy
from sqlalchemy import MetaData

from .types import EnumNamesToValues


def get_enum_values(enum_type: sqlalchemy.Enum) -> Tuple[str, ...]:
    """Extract enum values from SQLAlchemy Enum type."""
    # Handle TypeDecorator wrapped enums
    if isinstance(enum_type, sqlalchemy.types.TypeDecorator):
        enum_type = enum_type.impl

    # If a Python Enum class was used, extract values from the enum class
    if hasattr(enum_type, 'python_type') and enum_type.python_type:
        python_enum_class = enum_type.python_type
        if hasattr(python_enum_class, '__members__'):
            return tuple(member.value for member in python_enum_class)

    # Otherwise, use the enums list directly (for string-based enums)
    return tuple(enum_type.enums)


def column_type_is_enum(column_type: Any) -> bool:
    """Check if a column type is a PostgreSQL enum."""
    if isinstance(column_type, sqlalchemy.Enum):
        return column_type.native_enum

    # For specific case when types.TypeDecorator is used
    if isinstance(getattr(column_type, "impl", None), sqlalchemy.Enum):
        return True

    return False


def get_declared_enums(
    metadata: Union[MetaData, List[MetaData]],
    schema: str,
    default_schema: str,
    include_name: Optional[Callable[[str], bool]] = None,
) -> EnumNamesToValues:
    """
    Return a dict mapping SQLAlchemy declared enumeration types to their values.

    Args:
        metadata: SQLAlchemy schema metadata
        schema: Schema name (e.g. "public")
        default_schema: Default schema name
        include_name: Optional filter function for enum names

    Returns:
        Dict mapping enum names to their values: {"my_enum": ("a", "b", "c")}
    """
    if include_name is None:
        def include_name(_):
            return True

    enum_name_to_values = {}

    if isinstance(metadata, list):
        metadata_list = metadata
    else:
        metadata_list = [metadata]

    for metadata in metadata_list:
        for table in metadata.tables.values():
            for column in table.columns:
                column_type = column.type

                # Handle array of enums
                if isinstance(column_type, sqlalchemy.ARRAY):
                    column_type = column_type.item_type

                if not column_type_is_enum(column_type):
                    continue

                if not include_name(column_type.name):
                    continue

                column_type_schema = column_type.schema or default_schema
                if column_type_schema != schema:
                    continue

                if column_type.name not in enum_name_to_values:
                    enum_name_to_values[column_type.name] = get_enum_values(column_type)

    return enum_name_to_values
