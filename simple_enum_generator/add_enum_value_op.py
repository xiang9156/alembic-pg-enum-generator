from typing import TYPE_CHECKING

import alembic.operations.ops
import alembic.operations.base
import alembic.autogenerate.render
import sqlalchemy

from .connection import get_connection

if TYPE_CHECKING:
    from alembic.autogenerate.api import AutogenContext


@alembic.operations.base.Operations.register_operation("add_enum_value")
class AddEnumValueOp(alembic.operations.ops.MigrateOperation):
    """Operation to add a single value to an existing PostgreSQL enum type."""
    
    def __init__(self, enum_schema: str, enum_name: str, value: str):
        self.enum_schema = enum_schema
        self.enum_name = enum_name
        self.value = value

    @classmethod
    def add_enum_value(cls, operations, enum_schema: str, enum_name: str, value: str):
        """Execute the add enum value operation."""
        op = cls(enum_schema, enum_name, value)
        return operations.invoke(op)

    def reverse(self):
        """Reverse operation - not supported for add-only library."""
        raise NotImplementedError("Enum value removal is not supported")

    def execute(self, connection):
        """Execute the ALTER TYPE ... ADD VALUE statement."""
        if self.enum_schema:
            enum_type_name = f'"{self.enum_schema}"."{self.enum_name}"'
        else:
            enum_type_name = f'"{self.enum_name}"'
            
        connection.execute(
            sqlalchemy.text(f"ALTER TYPE {enum_type_name} ADD VALUE '{self.value}'")
        )


@alembic.autogenerate.render.renderers.dispatch_for(AddEnumValueOp)
def render_add_enum_value_op(autogen_context: "AutogenContext", op: AddEnumValueOp):
    """Render the add enum value operation in migration files."""
    return f"op.add_enum_value({op.enum_schema!r}, {op.enum_name!r}, {op.value!r})"