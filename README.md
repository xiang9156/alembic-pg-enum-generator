# Alembic PostgreSQL Enum Generator

[![CI](https://github.com/xiang9156/alembic-pg-enum-generator/workflows/CI/badge.svg)](https://github.com/xiang9156/alembic-pg-enum-generator/actions)
[![PyPI version](https://badge.fury.io/py/alembic-pg-enum-generator.svg)](https://badge.fury.io/py/alembic-pg-enum-generator)
[![Python versions](https://img.shields.io/pypi/pyversions/alembic-pg-enum-generator.svg)](https://pypi.org/project/alembic-pg-enum-generator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code coverage](https://codecov.io/gh/xiang9156/alembic-pg-enum-generator/branch/main/graph/badge.svg)](https://codecov.io/gh/xiang9156/alembic-pg-enum-generator)

A lightweight Alembic extension for PostgreSQL enum value additions.

## Why Use This?

Unlike complex enum sync libraries that use heavy "replace-and-cast" approaches causing **table locks** and **full table scans**, this library uses PostgreSQL's efficient `ALTER TYPE ... ADD VALUE` statement for:

- ✅ **No table locking** - only brief enum type locks
- ✅ **Production-safe** - minimal database impact  
- ✅ **Lightning fast** - no data conversion required
- ✅ **Add-only operations** - perfect for compatibility-focused environments

## Installation

```bash
pip install alembic-pg-enum-generator
```

## Usage

### 1. Import in your Alembic env.py

```python
# In your alembic/env.py file
import alembic_pg_enum_generator

# The import automatically registers with Alembic's autogenerate system
```

### 2. Define your enums in SQLAlchemy

```python
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"  # Add this new value

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    status = Column(Enum(UserStatus, name='user_status'))
```

### 3. Generate migration

```bash
alembic revision --autogenerate -m "Add pending status to user_status enum"
```

### 4. Generated migration

```python
"""Add pending status to user_status enum

Revision ID: abc123
Revises: def456
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op

def upgrade():
    # Simple, efficient ALTER TYPE statement
    op.add_enum_value('public', 'user_status', 'pending')

def downgrade():
    # Downgrade not supported for compatibility
    pass
```

## Configuration

### Filter enum names

```python
import alembic_pg_enum_generator

# Only process enums matching certain patterns
config = alembic_pg_enum_generator.Config(
    include_name=lambda name: name.startswith('app_')
)
alembic_pg_enum_generator.set_configuration(config)
```

## Features

### ✅ What it does
- Automatically detects new enum values in SQLAlchemy models
- Generates efficient `ALTER TYPE ... ADD VALUE` statements
- Integrates seamlessly with Alembic's autogenerate
- Works with multiple schemas
- Supports TypeDecorator wrapped enums
- Handles array columns with enums

### ❌ What it doesn't do
- No enum value deletion (use manual migrations for compatibility)
- No enum value reordering (PostgreSQL doesn't support this anyway)
- No enum renaming (use manual migrations)
- No downgrade support (enum additions are permanent for compatibility)

## Performance Comparison

| Operation | Alembic PG Enum Generator | Heavy Sync Libraries |
|-----------|----------------------|---------------------|
| SQL Command | `ALTER TYPE enum_name ADD VALUE 'new_value'` | Complex replace-and-cast with temp types |
| Table Lock | ❌ None | ✅ ACCESS EXCLUSIVE (blocks all operations) |
| Data Scan | ❌ None | ✅ Full table scan + rewrite |
| Production Impact | 🟢 Minimal (milliseconds) | 🔴 High (minutes on large tables) |

## Example: Adding Multiple Values

```python
# Before
class Priority(Enum):
    LOW = "low"
    HIGH = "high"

# After  
class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"    # New value 1
    HIGH = "high"
    CRITICAL = "critical"  # New value 2
```

Generated migration:
```python
def upgrade():
    op.add_enum_value('public', 'priority', 'medium')
    op.add_enum_value('public', 'priority', 'critical')
```

## Requirements

- Python 3.8+ (including 3.13)
- Alembic 1.0+
- SQLAlchemy 1.4+
- PostgreSQL (any version supporting ALTER TYPE ... ADD VALUE)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/xiang9156/alembic-pg-enum-generator.git
cd alembic-pg-enum-generator
```

2. Install dependencies with uv:
```bash
uv sync --all-extras --dev
```

3. Set up pre-commit hooks:
```bash
uv run pre-commit install
```

4. Run tests:
```bash
uv run pytest
```

### Code Quality

- **Linting**: `uv run ruff check .`
- **Formatting**: `uv run ruff format .`
- **Type checking**: `uv run mypy alembic_pg_enum_generator`
- **Tests**: `uv run pytest --cov=alembic_pg_enum_generator`

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for details about changes in each version.

## License

MIT License - see [LICENSE](LICENSE) file for details.