"""Tests for add_enum_value_op module."""

from unittest.mock import Mock

import pytest
import sqlalchemy

from alembic_pg_enum_generator.add_enum_value_op import AddEnumValueOp


class TestAddEnumValueOp:
    def test_init(self):
        """Test AddEnumValueOp initialization."""
        op = AddEnumValueOp("public", "user_status", "pending")

        assert op.enum_schema == "public"
        assert op.enum_name == "user_status"
        assert op.value == "pending"

    def test_init_no_schema(self):
        """Test AddEnumValueOp initialization without schema."""
        op = AddEnumValueOp(None, "user_status", "pending")

        assert op.enum_schema is None
        assert op.enum_name == "user_status"
        assert op.value == "pending"

    def test_reverse_not_implemented(self):
        """Test that reverse operation raises NotImplementedError."""
        op = AddEnumValueOp("public", "user_status", "pending")

        with pytest.raises(
            NotImplementedError, match="Enum value removal is not supported"
        ):
            op.reverse()

    def test_execute_with_schema(self):
        """Test execute method with schema."""
        mock_connection = Mock()
        op = AddEnumValueOp("public", "user_status", "pending")

        op.execute(mock_connection)

        # Verify the correct SQL was executed
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0][0]

        assert isinstance(call_args, sqlalchemy.sql.elements.TextClause)
        assert 'ALTER TYPE "public"."user_status" ADD VALUE \'pending\'' in str(
            call_args
        )

    def test_execute_without_schema(self):
        """Test execute method without schema."""
        mock_connection = Mock()
        op = AddEnumValueOp(None, "user_status", "pending")

        op.execute(mock_connection)

        # Verify the correct SQL was executed
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0][0]

        assert isinstance(call_args, sqlalchemy.sql.elements.TextClause)
        assert "ALTER TYPE \"user_status\" ADD VALUE 'pending'" in str(call_args)

    def test_execute_with_special_characters(self):
        """Test execute method with special characters in value."""
        mock_connection = Mock()
        op = AddEnumValueOp("public", "user_status", "pending-review")

        op.execute(mock_connection)

        # Verify the correct SQL was executed
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0][0]

        assert 'ALTER TYPE "public"."user_status" ADD VALUE \'pending-review\'' in str(
            call_args
        )

    def test_add_enum_value_classmethod(self):
        """Test the add_enum_value classmethod."""
        mock_operations = Mock()
        mock_operations.invoke.return_value = "result"

        result = AddEnumValueOp.add_enum_value(
            mock_operations, "public", "user_status", "pending"
        )

        # Verify invoke was called with correct operation
        mock_operations.invoke.assert_called_once()
        op = mock_operations.invoke.call_args[0][0]

        assert isinstance(op, AddEnumValueOp)
        assert op.enum_schema == "public"
        assert op.enum_name == "user_status"
        assert op.value == "pending"
        assert result == "result"

    def test_render_function(self):
        """Test the render function directly."""
        from alembic_pg_enum_generator.add_enum_value_op import render_add_enum_value_op

        mock_autogen_context = Mock()
        op = AddEnumValueOp("public", "user_status", "pending")

        result = render_add_enum_value_op(mock_autogen_context, op)

        expected = "op.add_enum_value('public', 'user_status', 'pending')"
        assert result == expected

    def test_render_function_no_schema(self):
        """Test the render function without schema."""
        from alembic_pg_enum_generator.add_enum_value_op import render_add_enum_value_op

        mock_autogen_context = Mock()
        op = AddEnumValueOp(None, "user_status", "pending")

        result = render_add_enum_value_op(mock_autogen_context, op)

        expected = "op.add_enum_value(None, 'user_status', 'pending')"
        assert result == expected

    def test_render_function_with_special_characters(self):
        """Test the render function with special characters."""
        from alembic_pg_enum_generator.add_enum_value_op import render_add_enum_value_op

        mock_autogen_context = Mock()
        op = AddEnumValueOp("my-schema", "user_status", "pending-review")

        result = render_add_enum_value_op(mock_autogen_context, op)

        expected = "op.add_enum_value('my-schema', 'user_status', 'pending-review')"
        assert result == expected
