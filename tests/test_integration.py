"""Integration tests for the complete enum detection and operation generation."""
import pytest
from enum import Enum as PyEnum
from unittest.mock import Mock, patch
from sqlalchemy import Column, Integer, String, Enum, MetaData, Table

from alembic_pg_enum_generator.compare_dispatch import compare_enums_for_additions
from alembic_pg_enum_generator.add_enum_value_op import AddEnumValueOp
from alembic_pg_enum_generator.config import Config, set_configuration


class UserStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive" 
    PENDING = "pending"


class OrderStatus(PyEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    SHIPPED = "shipped"


class MockUpgradeOps:
    def __init__(self):
        self.ops = []


class MockConnection:
    def __init__(self):
        self.dialect = Mock()
        self.dialect.name = "postgresql"
        self.dialect.default_schema_name = "public"


class MockAutogenContext:
    def __init__(self, metadata, defined_enums):
        self.metadata = metadata
        self.connection = MockConnection()
        self._defined_enums = defined_enums


class TestIntegration:
    def teardown_method(self):
        """Reset global configuration after each test."""
        import alembic_pg_enum_generator.config
        alembic_pg_enum_generator.config._configuration = None

    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_end_to_end_single_new_value(self, mock_get_defined):
        """Test complete flow from SQLAlchemy model to operation generation."""
        # Setup: Create SQLAlchemy metadata with enum
        metadata = MetaData()
        Table(
            'users',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('status', Enum(UserStatus, name='user_status', native_enum=True)),
            schema='public'
        )
        
        # Mock: Database only has 'active', 'inactive' 
        mock_get_defined.return_value = {
            'user_status': ('active', 'inactive')
        }
        
        # Execute: Run the comparison
        autogen_context = MockAutogenContext(metadata, {})
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, ['public'])
        
        # Verify: Should generate operation for 'pending'
        assert len(upgrade_ops.ops) == 1
        op = upgrade_ops.ops[0]
        assert isinstance(op, AddEnumValueOp)
        assert op.enum_schema == 'public'
        assert op.enum_name == 'user_status'
        assert op.value == 'pending'

    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_end_to_end_multiple_enums(self, mock_get_defined):
        """Test complete flow with multiple enums and new values."""
        # Setup: Create SQLAlchemy metadata with multiple enums
        metadata = MetaData()
        
        Table(
            'users',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('status', Enum(UserStatus, name='user_status', native_enum=True)),
            schema='public'
        )
        
        Table(
            'orders',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('status', Enum(OrderStatus, name='order_status', native_enum=True)),
            schema='public'
        )
        
        # Mock: Database has partial values for both enums
        mock_get_defined.return_value = {
            'user_status': ('active', 'inactive'),  # Missing 'pending'
            'order_status': ('draft', 'submitted')  # Missing 'processing', 'shipped'
        }
        
        # Execute: Run the comparison
        autogen_context = MockAutogenContext(metadata, {})
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, ['public'])
        
        # Verify: Should generate operations for all new values
        assert len(upgrade_ops.ops) == 3
        
        # Group operations by enum name
        ops_by_enum = {}
        for op in upgrade_ops.ops:
            if op.enum_name not in ops_by_enum:
                ops_by_enum[op.enum_name] = []
            ops_by_enum[op.enum_name].append(op.value)
        
        assert 'user_status' in ops_by_enum
        assert ops_by_enum['user_status'] == ['pending']
        
        assert 'order_status' in ops_by_enum
        assert set(ops_by_enum['order_status']) == {'processing', 'shipped'}

    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_end_to_end_with_filter(self, mock_get_defined):
        """Test complete flow with include_name filter."""
        # Setup: Configure filter to only include enums ending with '_status'
        config = Config(include_name=lambda name: name.endswith('_status'))
        set_configuration(config)
        
        # Setup: Create SQLAlchemy metadata with multiple enums
        metadata = MetaData()
        
        Table(
            'users',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('status', Enum(UserStatus, name='user_status', native_enum=True)),
            Column('priority', Enum(OrderStatus, name='user_priority', native_enum=True)),  # Should be filtered out
            schema='public'
        )
        
        # Mock: Database has partial values
        mock_get_defined.return_value = {
            'user_status': ('active', 'inactive'),
            'user_priority': ('draft', 'submitted')
        }
        
        # Execute: Run the comparison
        autogen_context = MockAutogenContext(metadata, {})
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, ['public'])
        
        # Verify: Should only generate operation for 'user_status' (filtered)
        assert len(upgrade_ops.ops) == 1
        op = upgrade_ops.ops[0]
        assert op.enum_name == 'user_status'
        assert op.value == 'pending'

    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_end_to_end_no_operations_needed(self, mock_get_defined):
        """Test complete flow when no new values are needed."""
        # Setup: Create SQLAlchemy metadata
        metadata = MetaData()
        Table(
            'users',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('status', Enum(UserStatus, name='user_status', native_enum=True)),
            schema='public'
        )
        
        # Mock: Database already has all values
        mock_get_defined.return_value = {
            'user_status': ('active', 'inactive', 'pending')  # All values present
        }
        
        # Execute: Run the comparison
        autogen_context = MockAutogenContext(metadata, {})
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, ['public'])
        
        # Verify: No operations should be generated
        assert len(upgrade_ops.ops) == 0

    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_end_to_end_new_enum_ignored(self, mock_get_defined):
        """Test that completely new enums are ignored (let Alembic handle)."""
        # Setup: Create SQLAlchemy metadata with enum
        metadata = MetaData()
        Table(
            'users',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('status', Enum(UserStatus, name='user_status', native_enum=True)),
            schema='public'
        )
        
        # Mock: Database doesn't have the enum at all
        mock_get_defined.return_value = {}  # Enum doesn't exist in DB
        
        # Execute: Run the comparison
        autogen_context = MockAutogenContext(metadata, {})
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, ['public'])
        
        # Verify: No operations should be generated (let standard Alembic handle)
        assert len(upgrade_ops.ops) == 0

    def test_operation_sql_generation(self):
        """Test that generated operations produce correct SQL."""
        mock_connection = Mock()
        
        # Test with schema
        op = AddEnumValueOp('public', 'user_status', 'pending')
        op.execute(mock_connection)
        
        # Verify SQL was executed
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args[0][0]
        sql_text = str(call_args)
        
        assert 'ALTER TYPE "public"."user_status" ADD VALUE \'pending\'' in sql_text

    def test_operation_rendering(self):
        """Test that operations render correctly in migration files."""
        from alembic_pg_enum_generator.add_enum_value_op import render_add_enum_value_op
        
        mock_autogen_context = Mock()
        op = AddEnumValueOp('public', 'user_status', 'pending')
        
        rendered = render_add_enum_value_op(mock_autogen_context, op)
        
        expected = "op.add_enum_value('public', 'user_status', 'pending')"
        assert rendered == expected

    @patch('simple_enum_generator.compare_dispatch.get_defined_enums')
    def test_schema_none_handling(self, mock_get_defined):
        """Test handling of None schema in integration."""
        # Setup: Create SQLAlchemy metadata
        metadata = MetaData()
        Table(
            'users',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('status', Enum(UserStatus, name='user_status', native_enum=True)),
            schema='public'
        )
        
        # Mock: Database has partial values
        mock_get_defined.return_value = {
            'user_status': ('active', 'inactive')
        }
        
        # Execute: Run with None schema (should use default)
        autogen_context = MockAutogenContext(metadata, {})
        upgrade_ops = MockUpgradeOps()
        
        compare_enums_for_additions(autogen_context, upgrade_ops, [None])
        
        # Verify: Should work with default schema
        assert len(upgrade_ops.ops) == 1
        op = upgrade_ops.ops[0]
        assert op.enum_schema == 'public'  # Should use default schema