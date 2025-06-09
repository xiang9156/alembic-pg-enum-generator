from typing import TYPE_CHECKING, Any

import alembic.autogenerate.render
import alembic.operations.base
import alembic.operations.ops
import sqlalchemy

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
    def add_enum_value(
        cls, operations: Any, enum_schema: str, enum_name: str, value: str
    ) -> Any:
        """Execute the add enum value operation."""
        op = cls(enum_schema, enum_name, value)
        return operations.invoke(op)

    def reverse(self) -> "alembic.operations.ops.MigrateOperation":
        """Reverse operation - not supported for add-only library."""
        # Return a no-op operation that does nothing
        from alembic.operations.ops import ExecuteSQLOp

        return ExecuteSQLOp("-- No-op: enum value removal not supported")

    def execute(self, connection: Any) -> None:
        """Execute the ALTER TYPE ... ADD VALUE statement."""
        if self.enum_schema:
            enum_type_name = f"{self.enum_schema}.{self.enum_name}"
        else:
            enum_type_name = self.enum_name

        connection.execute(
            sqlalchemy.text(f"ALTER TYPE {enum_type_name} ADD VALUE '{self.value}'")
        )


@alembic.autogenerate.render.renderers.dispatch_for(AddEnumValueOp)
def render_add_enum_value_op(
    autogen_context: "AutogenContext", op: AddEnumValueOp
) -> str:
    """Render the add enum value operation in migration files."""
    if op.enum_schema:
        enum_type_name = f"{op.enum_schema}.{op.enum_name}"
    else:
        enum_type_name = op.enum_name

    sql = f"ALTER TYPE {enum_type_name} ADD VALUE '{op.value}'"
    return f'op.execute("{sql}")'
