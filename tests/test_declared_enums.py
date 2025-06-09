"""Tests for declared_enums module."""

from enum import Enum as PyEnum

from sqlalchemy import ARRAY, Column, Enum, Integer, MetaData, String, Table
from sqlalchemy.types import TypeDecorator

from alembic_pg_enum_generator.declared_enums import (
    column_type_is_enum,
    get_declared_enums,
    get_enum_values,
)


class TestStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class OrderStatus(PyEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"


class CustomTypeDecorator(TypeDecorator):
    impl = Enum
    cache_ok = True

    def __init__(self):
        super().__init__(TestStatus, name="custom_status")


class TestGetEnumValues:
    def test_get_enum_values_basic(self):
        """Test extracting values from a basic SQLAlchemy Enum."""
        enum_type = Enum(TestStatus, name="test_status")
        values = get_enum_values(enum_type)
        assert values == ("active", "inactive", "pending")

    def test_get_enum_values_with_strings(self):
        """Test extracting values from enum defined with string values."""
        enum_type = Enum("draft", "submitted", "shipped", name="order_status")
        values = get_enum_values(enum_type)
        assert values == ("draft", "submitted", "shipped")

    def test_get_enum_values_type_decorator(self):
        """Test extracting values from TypeDecorator wrapped enum."""
        enum_type = CustomTypeDecorator()
        values = get_enum_values(enum_type)
        assert values == ("active", "inactive", "pending")


class TestColumnTypeIsEnum:
    def test_column_type_is_enum_true(self):
        """Test that native enum columns are detected."""
        enum_type = Enum(TestStatus, name="test_status", native_enum=True)
        assert column_type_is_enum(enum_type) is True

    def test_column_type_is_enum_false_non_native(self):
        """Test that non-native enum columns are not detected."""
        enum_type = Enum(TestStatus, name="test_status", native_enum=False)
        assert column_type_is_enum(enum_type) is False

    def test_column_type_is_enum_false_non_enum(self):
        """Test that non-enum columns are not detected."""
        assert column_type_is_enum(String(50)) is False
        assert column_type_is_enum(Integer()) is False

    def test_column_type_is_enum_type_decorator(self):
        """Test that TypeDecorator wrapped enums are detected."""
        enum_type = CustomTypeDecorator()
        assert column_type_is_enum(enum_type) is True


class TestGetDeclaredEnums:
    def test_get_declared_enums_single_table(self):
        """Test detecting enums from a single table."""
        metadata = MetaData()

        Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("status", Enum(TestStatus, name="user_status", native_enum=True)),
            schema="public",
        )

        declared_enums = get_declared_enums(
            metadata=metadata, schema="public", default_schema="public"
        )

        assert "user_status" in declared_enums
        assert declared_enums["user_status"] == ("active", "inactive", "pending")

    def test_get_declared_enums_multiple_tables(self):
        """Test detecting enums from multiple tables."""
        metadata = MetaData()

        Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("status", Enum(TestStatus, name="user_status", native_enum=True)),
            schema="public",
        )

        Table(
            "orders",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("status", Enum(OrderStatus, name="order_status", native_enum=True)),
            schema="public",
        )

        declared_enums = get_declared_enums(
            metadata=metadata, schema="public", default_schema="public"
        )

        assert "user_status" in declared_enums
        assert "order_status" in declared_enums
        assert declared_enums["user_status"] == ("active", "inactive", "pending")
        assert declared_enums["order_status"] == ("draft", "submitted")

    def test_get_declared_enums_array_column(self):
        """Test detecting enums used in array columns."""
        metadata = MetaData()

        Table(
            "tags",
            metadata,
            Column("id", Integer, primary_key=True),
            Column(
                "statuses", ARRAY(Enum(TestStatus, name="tag_status", native_enum=True))
            ),
            schema="public",
        )

        declared_enums = get_declared_enums(
            metadata=metadata, schema="public", default_schema="public"
        )

        assert "tag_status" in declared_enums
        assert declared_enums["tag_status"] == ("active", "inactive", "pending")

    def test_get_declared_enums_different_schema(self):
        """Test that enums in different schemas are ignored."""
        metadata = MetaData()

        Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column(
                "status",
                Enum(
                    TestStatus,
                    name="user_status",
                    native_enum=True,
                    schema="other_schema",
                ),
            ),
            schema="public",
        )

        declared_enums = get_declared_enums(
            metadata=metadata,
            schema="public",  # Looking for enums in public schema
            default_schema="public",
        )

        # Should not find the enum since it's in 'other_schema'
        assert "user_status" not in declared_enums

    def test_get_declared_enums_with_filter(self):
        """Test filtering enums by name."""
        metadata = MetaData()

        Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("status", Enum(TestStatus, name="user_status", native_enum=True)),
            Column(
                "priority", Enum(OrderStatus, name="user_priority", native_enum=True)
            ),
            schema="public",
        )

        # Only include enums ending with '_status'
        def status_filter(name):
            return name.endswith("_status")

        declared_enums = get_declared_enums(
            metadata=metadata,
            schema="public",
            default_schema="public",
            include_name=status_filter,
        )

        assert "user_status" in declared_enums
        assert "user_priority" not in declared_enums

    def test_get_declared_enums_non_native_ignored(self):
        """Test that non-native enums are ignored."""
        metadata = MetaData()

        Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column(
                "status", Enum(TestStatus, name="user_status", native_enum=False)
            ),  # Not native
            schema="public",
        )

        declared_enums = get_declared_enums(
            metadata=metadata, schema="public", default_schema="public"
        )

        # Should not find the enum since it's not native
        assert "user_status" not in declared_enums

    def test_get_declared_enums_metadata_list(self):
        """Test handling multiple metadata objects."""
        metadata1 = MetaData()
        metadata2 = MetaData()

        Table(
            "users",
            metadata1,
            Column("id", Integer, primary_key=True),
            Column("status", Enum(TestStatus, name="user_status", native_enum=True)),
            schema="public",
        )

        Table(
            "orders",
            metadata2,
            Column("id", Integer, primary_key=True),
            Column("status", Enum(OrderStatus, name="order_status", native_enum=True)),
            schema="public",
        )

        declared_enums = get_declared_enums(
            metadata=[metadata1, metadata2], schema="public", default_schema="public"
        )

        assert "user_status" in declared_enums
        assert "order_status" in declared_enums
