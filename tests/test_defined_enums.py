"""Tests for defined_enums module."""

from unittest.mock import Mock

from alembic_pg_enum_generator.defined_enums import (
    _extract_enum_name,
    get_all_enums,
    get_defined_enums,
)


class TestExtractEnumName:
    def test_extract_enum_name_no_schema(self):
        """Test extracting enum name without schema prefix."""
        result = _extract_enum_name("user_status", "public")
        assert result == "user_status"

    def test_extract_enum_name_with_schema(self):
        """Test extracting enum name with schema prefix."""
        result = _extract_enum_name("public.user_status", "public")
        assert result == "user_status"

    def test_extract_enum_name_with_quoted_schema(self):
        """Test extracting enum name with quoted schema prefix."""
        result = _extract_enum_name('"public".user_status', "public")
        assert result == "user_status"

    def test_extract_enum_name_with_quotes(self):
        """Test extracting enum name with quotes around name."""
        result = _extract_enum_name('"user_status"', "public")
        assert result == "user_status"

    def test_extract_enum_name_with_schema_and_quotes(self):
        """Test extracting enum name with both schema and quotes."""
        result = _extract_enum_name('"public"."user_status"', "public")
        assert result == "user_status"

    def test_extract_enum_name_different_schema(self):
        """Test extracting enum name with different schema."""
        result = _extract_enum_name("other_schema.user_status", "public")
        assert result == "other_schema.user_status"  # Should not strip different schema


class TestGetAllEnums:
    def test_get_all_enums_sql_query(self):
        """Test that get_all_enums executes the correct SQL query."""
        mock_connection = Mock()
        mock_result = Mock()
        mock_connection.execute.return_value = mock_result

        result = get_all_enums(mock_connection, "public")

        # Verify the SQL query was executed
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args

        # Check that it's a text query with schema parameter
        assert "pg_catalog.pg_type" in str(call_args.args[0])
        assert "pg_catalog.pg_enum" in str(call_args.args[0])
        assert call_args.args[1] == {"schema": "public"}
        assert result == mock_result


class TestGetDefinedEnums:
    def test_get_defined_enums_empty_result(self):
        """Test get_defined_enums with no enums in database."""
        mock_connection = Mock()
        mock_connection.execute.return_value = []

        result = get_defined_enums(mock_connection, "public")

        assert result == {}

    def test_get_defined_enums_single_enum(self):
        """Test get_defined_enums with single enum."""
        mock_connection = Mock()
        mock_connection.execute.return_value = [
            ("user_status", ["active", "inactive", "pending"])
        ]

        result = get_defined_enums(mock_connection, "public")

        assert result == {"user_status": ("active", "inactive", "pending")}

    def test_get_defined_enums_multiple_enums(self):
        """Test get_defined_enums with multiple enums."""
        mock_connection = Mock()
        mock_connection.execute.return_value = [
            ("user_status", ["active", "inactive"]),
            ("order_status", ["draft", "submitted", "shipped"]),
        ]

        result = get_defined_enums(mock_connection, "public")

        assert result == {
            "user_status": ("active", "inactive"),
            "order_status": ("draft", "submitted", "shipped"),
        }

    def test_get_defined_enums_with_schema_prefix(self):
        """Test get_defined_enums with schema prefixed enum names."""
        mock_connection = Mock()
        mock_connection.execute.return_value = [
            ("public.user_status", ["active", "inactive"]),
            ('"public".order_status', ["draft", "submitted"]),
        ]

        result = get_defined_enums(mock_connection, "public")

        assert result == {
            "user_status": ("active", "inactive"),
            "order_status": ("draft", "submitted"),
        }

    def test_get_defined_enums_with_filter(self):
        """Test get_defined_enums with include_name filter."""
        mock_connection = Mock()
        mock_connection.execute.return_value = [
            ("user_status", ["active", "inactive"]),
            ("user_priority", ["low", "high"]),
            ("order_status", ["draft", "submitted"]),
        ]

        # Only include enums ending with '_status'
        def status_filter(name):
            return name.endswith("_status")

        result = get_defined_enums(
            mock_connection,
            "public",
            include_name=status_filter,
        )

        assert result == {
            "user_status": ("active", "inactive"),
            "order_status": ("draft", "submitted"),
        }
        assert "user_priority" not in result

    def test_get_defined_enums_with_quotes(self):
        """Test get_defined_enums with quoted enum names."""
        mock_connection = Mock()
        mock_connection.execute.return_value = [
            ('"user_status"', ["active", "inactive"]),
            ('"order-status"', ["draft", "submitted"]),  # Hyphenated name
        ]

        result = get_defined_enums(mock_connection, "public")

        assert result == {
            "user_status": ("active", "inactive"),
            "order-status": ("draft", "submitted"),
        }

    def test_get_defined_enums_empty_enum(self):
        """Test get_defined_enums with enum that has no values."""
        mock_connection = Mock()
        mock_connection.execute.return_value = [("empty_status", [])]

        result = get_defined_enums(mock_connection, "public")

        assert result == {"empty_status": ()}

    def test_get_defined_enums_default_filter(self):
        """Test get_defined_enums with default include_name (no filter)."""
        mock_connection = Mock()
        mock_connection.execute.return_value = [
            ("user_status", ["active"]),
            ("_internal_enum", ["value"]),
            ("123_numeric", ["test"]),
        ]

        result = get_defined_enums(mock_connection, "public")

        # All enums should be included with default filter
        assert len(result) == 3
        assert "user_status" in result
        assert "_internal_enum" in result
        assert "123_numeric" in result
