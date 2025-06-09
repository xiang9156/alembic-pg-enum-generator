from typing import TYPE_CHECKING, Callable, Optional

import sqlalchemy

from .types import EnumNamesToValues

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection


def _extract_enum_name(enum_name: str, schema: str) -> str:
    """Extract enum name by removing schema prefix and quotes."""
    # Remove schema
    schema_prefix = f"{schema}."
    quoted_schema_prefix = f'"{schema}".'
    if enum_name.startswith(schema_prefix):
        enum_name = enum_name[len(schema_prefix) :]
    elif enum_name.startswith(quoted_schema_prefix):
        enum_name = enum_name[len(quoted_schema_prefix) :]

    # Remove quotes
    if enum_name.startswith('"') and enum_name.endswith('"'):
        enum_name = enum_name[1:-1]

    return enum_name


def get_all_enums(connection: "Connection", schema: str):
    """Query PostgreSQL for all enum types and their values in a schema."""
    sql = """
        SELECT
            pg_catalog.format_type(t.oid, NULL),
            ARRAY(SELECT enumlabel
                  FROM pg_catalog.pg_enum
                  WHERE enumtypid = t.oid
                  ORDER BY enumsortorder)
        FROM pg_catalog.pg_type t
        LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE
            t.typtype = 'e'
            AND n.nspname = :schema
    """
    return connection.execute(sqlalchemy.text(sql), {"schema": schema})


def get_defined_enums(
    connection: "Connection",
    schema: str,
    include_name: Optional[Callable[[str], bool]] = None,
) -> EnumNamesToValues:
    """
    Return a dict mapping PostgreSQL defined enumeration types to their values.

    Args:
        connection: SQLAlchemy connection instance
        schema: Schema name (e.g. "public")
        include_name: Optional filter function for enum names

    Returns:
        Dict mapping enum names to their values: {"my_enum": ("a", "b", "c")}
    """
    if include_name is None:

        def include_name(_):
            return True

    return {
        enum_name: tuple(values)
        for enum_name, values in (
            (_extract_enum_name(name, schema), values)
            for name, values in get_all_enums(connection, schema)
        )
        if include_name(enum_name)
    }
