# Contributing to Simple Enum Generator

Thank you for your interest in contributing to Simple Enum Generator! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- PostgreSQL (for integration tests)

### Development Setup

1. **Fork and clone the repository:**
```bash
git clone https://github.com/xiang9156/simple-enum-generator.git
cd simple-enum-generator
```

2. **Install dependencies:**
```bash
uv sync --all-extras --dev
```

3. **Set up pre-commit hooks:**
```bash
uv run pre-commit install
```

4. **Verify installation:**
```bash
uv run pytest
```

## Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Pre-commit** for automated checks

Run these commands before committing:

```bash
# Format code
uv run ruff format .

# Check and fix linting issues
uv run ruff check . --fix

# Type checking
uv run mypy simple_enum_generator

# Run tests
uv run pytest
```

### Testing

We maintain high test coverage. Please ensure all new code is tested:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=simple_enum_generator --cov-report=html

# Run specific test file
uv run pytest tests/test_your_feature.py

# Run with verbose output
uv run pytest -v
```

### Test Categories

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test complete workflows
3. **Mock Tests**: Test Alembic integration without database

## Contributing Guidelines

### Reporting Issues

When reporting bugs, please include:

- Python version
- Alembic version
- SQLAlchemy version
- PostgreSQL version
- Minimal reproduction case
- Expected vs actual behavior

### Feature Requests

Before implementing new features:

1. Open an issue to discuss the feature
2. Ensure it aligns with the project's goals
3. Consider backward compatibility
4. Think about test coverage

### Pull Requests

1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
   - Write clear, documented code
   - Add appropriate tests
   - Update documentation if needed

3. **Ensure quality:**
```bash
uv run ruff format .
uv run ruff check .
uv run mypy simple_enum_generator
uv run pytest
```

4. **Commit with clear messages:**
```bash
git commit -m "feat: add new enum filtering capability"
```

5. **Push and create PR:**
```bash
git push origin feature/your-feature-name
```

### Commit Message Format

Use conventional commits:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring
- `ci:` for CI/CD changes

## Project Structure

```
simple-enum-generator/
├── simple_enum_generator/          # Main package
│   ├── __init__.py                # Package entry point
│   ├── add_enum_value_op.py       # Custom Alembic operation
│   ├── compare_dispatch.py        # Alembic comparator integration
│   ├── declared_enums.py          # SQLAlchemy enum detection
│   ├── defined_enums.py           # PostgreSQL enum detection
│   ├── config.py                  # Configuration management
│   ├── connection.py              # SQLAlchemy compatibility
│   └── types.py                   # Type definitions
├── tests/                         # Test suite
│   ├── test_declared_enums.py     # Unit tests for enum detection
│   ├── test_defined_enums.py      # Unit tests for DB queries
│   ├── test_add_enum_value_op.py  # Unit tests for operations
│   ├── test_compare_dispatch.py   # Unit tests for comparator
│   ├── test_config.py             # Unit tests for configuration
│   └── test_integration.py        # Integration tests
├── example/                       # Usage examples
├── .github/workflows/             # CI/CD configuration
├── pyproject.toml                 # Project configuration
└── README.md                      # Project documentation
```

## Design Principles

### 1. Simplicity First
- Focus only on adding enum values
- Avoid complex features that increase maintenance burden
- Keep the API minimal and intuitive

### 2. Performance Oriented
- Use efficient `ALTER TYPE ... ADD VALUE` statements
- Avoid table-locking operations
- Minimize database impact

### 3. Alembic Integration
- Follow Alembic's plugin patterns
- Don't interfere with standard Alembic operations
- Provide clear migration output

### 4. Production Ready
- Handle edge cases gracefully
- Provide clear error messages
- Maintain backward compatibility

## What We Don't Accept

To maintain the project's focus and simplicity:

- **Enum value deletion** - Use manual migrations for compatibility
- **Enum value reordering** - PostgreSQL doesn't support this efficiently
- **Complex enum operations** - Keep it simple, add-only
- **Non-PostgreSQL support** - This is PostgreSQL-specific by design

## Release Process

1. Update version in `simple_enum_generator/__init__.py`
2. Update `CHANGELOG.md`
3. Create release PR
4. After merge, tag the release: `git tag v1.x.x`
5. Push tag: `git push origin v1.x.x`
6. GitHub Actions will handle PyPI publishing

## Getting Help

- Open an issue for bug reports
- Start a discussion for feature ideas
- Check existing issues before creating new ones
- Provide minimal reproduction cases

## Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Help others learn and grow
- Maintain a welcoming environment

Thank you for contributing to Simple Enum Generator!