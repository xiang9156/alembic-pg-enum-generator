"""
Simple Enum Generator - A lightweight Alembic extension for PostgreSQL enum additions.

This library provides automatic detection and generation of enum value additions
using PostgreSQL's efficient ALTER TYPE ... ADD VALUE statement.

Usage:
    Simply import this library in your Alembic env.py:

    import alembic_pg_enum_generator

    The import automatically registers the necessary hooks with Alembic's
    autogenerate system.

Features:
    - Automatic detection of new enum values
    - Efficient ALTER TYPE ... ADD VALUE SQL generation
    - No table locking (unlike complex enum sync operations)
    - Production-safe with minimal database locking
    - Add-only operations (no deletion/reordering for compatibility)
"""

from .add_enum_value_op import AddEnumValueOp

# Import the compare dispatch to register it with Alembic
# This import triggers the @dispatch_for decorator registration
from .compare_dispatch import compare_enums_for_additions as _
from .config import Config, get_configuration, set_configuration

__version__ = "1.0.0"

__all__ = [
    "Config",
    "get_configuration",
    "set_configuration",
    "AddEnumValueOp",
]
