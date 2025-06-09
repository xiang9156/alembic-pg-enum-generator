"""Tests for compare_dispatch module."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from simple_enum_generator.compare_dispatch import compare_enums_for_additions
from simple_enum_generator.add_enum_value_op import AddEnumValueOp


class MockUpgradeOps:
    def __init__(self):
        self.ops = []


class MockAutogenContext:
    def __init__(self, dialect_name="postgresql", metadata=None, connection=None):
        self.metadata = metadata or Mock()
        self.connection = Mock()
        self.connection.dialect.name = dialect_name
        self.connection.dialect.default_schema_name = "public"
        if connection:
            self.connection = connection


class TestCompareEnumsForAdditions:
    @patch('simple_enum_generator.compare_dispatch.get_configuration')
    @patch('simple_enum_generator.compare_dispatch.get_declared_enums')
    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_no_new_values(self, mock_get_defined, mock_get_declared, mock_get_config):
        """Test when there are no new enum values to add."""
        # Setup mocks
        mock_get_config.return_value = Mock(include_name=None)
        mock_get_declared.return_value = {
            "user_status": ("active", "inactive")
        }
        mock_get_defined.return_value = {
            "user_status": ("active", "inactive")
        }
        
        autogen_context = MockAutogenContext()
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, ["public"])
        
        # No operations should be added
        assert len(upgrade_ops.ops) == 0

    @patch('simple_enum_generator.compare_dispatch.get_configuration')
    @patch('simple_enum_generator.compare_dispatch.get_declared_enums')
    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_single_new_value(self, mock_get_defined, mock_get_declared, mock_get_config):
        """Test when there is a single new enum value to add."""
        # Setup mocks
        mock_get_config.return_value = Mock(include_name=None)
        mock_get_declared.return_value = {
            "user_status": ("active", "inactive", "pending")  # Has new 'pending'
        }
        mock_get_defined.return_value = {
            "user_status": ("active", "inactive")  # Missing 'pending'
        }
        
        autogen_context = MockAutogenContext()
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, ["public"])
        
        # One operation should be added
        assert len(upgrade_ops.ops) == 1
        op = upgrade_ops.ops[0]
        assert isinstance(op, AddEnumValueOp)
        assert op.enum_schema == "public"
        assert op.enum_name == "user_status"
        assert op.value == "pending"

    @patch('simple_enum_generator.compare_dispatch.get_configuration')
    @patch('simple_enum_generator.compare_dispatch.get_declared_enums')
    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_multiple_new_values(self, mock_get_defined, mock_get_declared, mock_get_config):
        """Test when there are multiple new enum values to add."""
        # Setup mocks
        mock_get_config.return_value = Mock(include_name=None)
        mock_get_declared.return_value = {
            "user_status": ("active", "inactive", "pending", "suspended")  # Two new values
        }
        mock_get_defined.return_value = {
            "user_status": ("active", "inactive")
        }
        
        autogen_context = MockAutogenContext()
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, ["public"])
        
        # Two operations should be added
        assert len(upgrade_ops.ops) == 2
        
        # Check that both new values are added
        values = {op.value for op in upgrade_ops.ops}
        assert "pending" in values
        assert "suspended" in values
        
        # All ops should be for the same enum
        for op in upgrade_ops.ops:
            assert isinstance(op, AddEnumValueOp)
            assert op.enum_schema == "public"
            assert op.enum_name == "user_status"

    @patch('simple_enum_generator.compare_dispatch.get_configuration')
    @patch('simple_enum_generator.compare_dispatch.get_declared_enums')
    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_multiple_enums(self, mock_get_defined, mock_get_declared, mock_get_config):
        """Test when multiple enums have new values."""
        # Setup mocks
        mock_get_config.return_value = Mock(include_name=None)
        mock_get_declared.return_value = {
            "user_status": ("active", "inactive", "pending"),
            "order_status": ("draft", "submitted", "shipped")
        }
        mock_get_defined.return_value = {
            "user_status": ("active", "inactive"),
            "order_status": ("draft", "submitted")
        }
        
        autogen_context = MockAutogenContext()
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, ["public"])
        
        # Two operations should be added
        assert len(upgrade_ops.ops) == 2
        
        # Check operations by enum name
        ops_by_enum = {op.enum_name: op for op in upgrade_ops.ops}
        
        assert "user_status" in ops_by_enum
        assert ops_by_enum["user_status"].value == "pending"
        
        assert "order_status" in ops_by_enum
        assert ops_by_enum["order_status"].value == "shipped"

    @patch('simple_enum_generator.compare_dispatch.get_configuration')
    @patch('simple_enum_generator.compare_dispatch.get_declared_enums')
    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_enum_not_in_database(self, mock_get_defined, mock_get_declared, mock_get_config):
        """Test when enum exists in code but not in database (should be skipped)."""
        # Setup mocks
        mock_get_config.return_value = Mock(include_name=None)
        mock_get_declared.return_value = {
            "user_status": ("active", "inactive", "pending"),
            "new_enum": ("value1", "value2")  # Enum not in database
        }
        mock_get_defined.return_value = {
            "user_status": ("active", "inactive")
            # "new_enum" not in database
        }
        
        autogen_context = MockAutogenContext()
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, ["public"])
        
        # Only one operation for existing enum
        assert len(upgrade_ops.ops) == 1
        op = upgrade_ops.ops[0]
        assert op.enum_name == "user_status"
        assert op.value == "pending"

    def test_non_postgresql_dialect(self):
        """Test that non-PostgreSQL dialects are ignored."""
        autogen_context = MockAutogenContext(dialect_name="mysql")
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, ["public"])
        
        # No operations should be added for non-PostgreSQL
        assert len(upgrade_ops.ops) == 0

    @patch('simple_enum_generator.compare_dispatch.get_configuration')
    @patch('simple_enum_generator.compare_dispatch.get_declared_enums')
    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_none_schema_handling(self, mock_get_defined, mock_get_declared, mock_get_config):
        """Test handling of None schema (should use default)."""
        # Setup mocks
        mock_get_config.return_value = Mock(include_name=None)
        mock_get_declared.return_value = {
            "user_status": ("active", "inactive", "pending")
        }
        mock_get_defined.return_value = {
            "user_status": ("active", "inactive")
        }
        
        autogen_context = MockAutogenContext()
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, [None])
        
        # Should process with default schema
        assert len(upgrade_ops.ops) == 1
        op = upgrade_ops.ops[0]
        assert op.enum_schema == "public"  # Default schema
        assert op.enum_name == "user_status"
        assert op.value == "pending"

    @patch('simple_enum_generator.compare_dispatch.get_configuration')
    @patch('simple_enum_generator.compare_dispatch.get_declared_enums')
    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_removed_values_ignored(self, mock_get_defined, mock_get_declared, mock_get_config):
        """Test that removed enum values are ignored (add-only behavior)."""
        # Setup mocks
        mock_get_config.return_value = Mock(include_name=None)
        mock_get_declared.return_value = {
            "user_status": ("active", "pending")  # Missing 'inactive' from code
        }
        mock_get_defined.return_value = {
            "user_status": ("active", "inactive", "suspended")  # Has extra values in DB
        }
        
        autogen_context = MockAutogenContext()
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, ["public"])
        
        # Only one operation for new value 'pending'
        assert len(upgrade_ops.ops) == 1
        op = upgrade_ops.ops[0]
        assert op.value == "pending"

    @patch('simple_enum_generator.compare_dispatch.get_configuration')
    @patch('simple_enum_generator.compare_dispatch.get_declared_enums')
    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_configuration_include_name_filter(self, mock_get_defined, mock_get_declared, mock_get_config):
        """Test that configuration include_name filter is passed through."""
        # Setup mocks
        include_name_filter = Mock()
        mock_get_config.return_value = Mock(include_name=include_name_filter)
        mock_get_declared.return_value = {}
        mock_get_defined.return_value = {}
        
        autogen_context = MockAutogenContext()
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, ["public"])
        
        # Verify the filter was passed to both functions
        mock_get_declared.assert_called_once_with(
            metadata=autogen_context.metadata,
            schema="public",
            default_schema="public",
            include_name=include_name_filter
        )
        mock_get_defined.assert_called_once_with(
            connection=autogen_context.connection,
            schema="public",
            include_name=include_name_filter
        )