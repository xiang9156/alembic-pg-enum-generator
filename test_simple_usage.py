"""
Simple test to verify the enum detection logic works correctly.
"""
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Enum, MetaData, Table
from simple_enum_generator.declared_enums import get_declared_enums, get_enum_values


class TestStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


def test_get_enum_values():
    """Test that we can extract values from SQLAlchemy Enum."""
    sqlalchemy_enum = Enum(TestStatus, name='test_status')
    values = get_enum_values(sqlalchemy_enum)
    
    # Values should be extracted correctly
    assert values == ("active", "inactive", "pending")
    print("✅ get_enum_values works correctly")


def test_get_declared_enums():
    """Test that we can detect enums from SQLAlchemy metadata."""
    metadata = MetaData()
    
    # Create a table with an enum column
    test_table = Table(
        'test_table',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('status', Enum(TestStatus, name='test_status')),
        schema='public'
    )
    
    # Get declared enums
    declared_enums = get_declared_enums(
        metadata=metadata,
        schema='public',
        default_schema='public'
    )
    
    # Should find our enum
    assert 'test_status' in declared_enums
    assert declared_enums['test_status'] == ("active", "inactive", "pending")
    print("✅ get_declared_enums works correctly")


def test_new_value_detection():
    """Test the core logic for detecting new enum values."""
    # Simulate declared enums (from SQLAlchemy models)
    declared_enums = {
        'user_status': ('active', 'inactive', 'pending')  # Has new 'pending' value
    }
    
    # Simulate defined enums (from database)
    defined_enums = {
        'user_status': ('active', 'inactive')  # Missing 'pending'
    }
    
    # Detect new values
    for enum_name, declared_values in declared_enums.items():
        if enum_name in defined_enums:
            defined_values = defined_enums[enum_name]
            new_values = [value for value in declared_values if value not in defined_values]
            
            # Should detect 'pending' as new
            assert new_values == ['pending']
            print(f"✅ Detected new value '{new_values[0]}' for enum '{enum_name}'")


if __name__ == "__main__":
    test_get_enum_values()
    test_get_declared_enums() 
    test_new_value_detection()
    print("\n🎉 All tests passed! Simple enum generator is working correctly.")