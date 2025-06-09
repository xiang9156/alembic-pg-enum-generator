from typing import Iterable, List, Union, cast

from alembic.autogenerate import comparators
from alembic.autogenerate.api import AutogenContext
from alembic.operations.ops import UpgradeOps
from sqlalchemy import MetaData

from .add_enum_value_op import AddEnumValueOp
from .config import get_configuration
from .declared_enums import get_declared_enums
from .defined_enums import get_defined_enums


@comparators.dispatch_for("schema")
def compare_enums_for_additions(
    autogen_context: AutogenContext,
    upgrade_ops: UpgradeOps,
    schema_names: Iterable[Union[str, None]],
) -> None:
    """
    Compare declared and defined enums to detect new values that need to be added.
    This is the main integration point with Alembic's autogenerate system.
    """
    config = get_configuration()

    # Check if we're using PostgreSQL
    connection = autogen_context.connection
    if connection is None or connection.dialect.name != "postgresql":
        return

    # Get default schema
    default_schema = connection.dialect.default_schema_name or "public"

    for schema in schema_names:
        if schema is None:
            schema = default_schema

        # Get declared enums from SQLAlchemy metadata
        metadata = autogen_context.metadata
        if metadata is None:
            continue

        # Convert metadata to the expected type
        if isinstance(metadata, list):
            metadata_list = cast(List[MetaData], metadata)
        else:
            metadata_list = [cast(MetaData, metadata)]

        declared_enums = get_declared_enums(
            metadata=metadata_list,
            schema=schema,
            default_schema=default_schema,
            include_name=config.include_name,
        )

        # Get defined enums from PostgreSQL database
        defined_enums = get_defined_enums(
            connection=connection,
            schema=schema,
            include_name=config.include_name,
        )

        # Compare and detect new values
        for enum_name, declared_values in declared_enums.items():
            if enum_name not in defined_enums:
                # Enum doesn't exist in database - skip (let standard Alembic handle enum creation)
                continue

            defined_values = defined_enums[enum_name]

            # Find new values (values in declared but not in defined)
            new_values = [
                value for value in declared_values if value not in defined_values
            ]

            # Generate AddEnumValueOp for each new value
            for value in new_values:
                upgrade_ops.ops.append(
                    AddEnumValueOp(
                        enum_schema=schema,
                        enum_name=enum_name,
                        value=value,
                    )
                )
