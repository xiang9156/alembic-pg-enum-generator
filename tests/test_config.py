"""Tests for config module."""
import pytest
from alembic_pg_enum_generator.config import Config, get_configuration, set_configuration


class TestConfig:
    def test_config_default_values(self):
        """Test Config dataclass default values."""
        config = Config()
        assert config.include_name is None

    def test_config_with_include_name(self):
        """Test Config with include_name filter."""
        filter_func = lambda name: name.endswith('_status')
        config = Config(include_name=filter_func)
        assert config.include_name == filter_func

    def test_config_callable_include_name(self):
        """Test that include_name can be any callable."""
        def custom_filter(name):
            return name.startswith('app_')
        
        config = Config(include_name=custom_filter)
        assert config.include_name == custom_filter
        assert config.include_name('app_status') is True
        assert config.include_name('user_status') is False


class TestConfigurationManagement:
    def teardown_method(self):
        """Reset global configuration after each test."""
        import alembic_pg_enum_generator.config
        alembic_pg_enum_generator.config._configuration = None

    def test_get_configuration_default(self):
        """Test get_configuration returns default Config when none set."""
        config = get_configuration()
        
        assert isinstance(config, Config)
        assert config.include_name is None

    def test_get_configuration_cached(self):
        """Test get_configuration returns the same instance when called multiple times."""
        config1 = get_configuration()
        config2 = get_configuration()
        
        assert config1 is config2

    def test_set_configuration(self):
        """Test set_configuration updates the global configuration."""
        custom_filter = lambda name: name.endswith('_enum')
        custom_config = Config(include_name=custom_filter)
        
        set_configuration(custom_config)
        
        retrieved_config = get_configuration()
        assert retrieved_config is custom_config
        assert retrieved_config.include_name == custom_filter

    def test_set_configuration_overwrites(self):
        """Test set_configuration overwrites previous configuration."""
        # Set first configuration
        config1 = Config(include_name=lambda name: True)
        set_configuration(config1)
        
        # Set second configuration
        config2 = Config(include_name=lambda name: False)
        set_configuration(config2)
        
        retrieved_config = get_configuration()
        assert retrieved_config is config2
        assert retrieved_config is not config1

    def test_configuration_isolation(self):
        """Test that configuration changes don't affect other instances."""
        # Get default config
        default_config = get_configuration()
        
        # Create and set custom config
        custom_config = Config(include_name=lambda name: name.startswith('test_'))
        set_configuration(custom_config)
        
        # The original default_config object should be unchanged
        assert default_config.include_name is None
        
        # But get_configuration should return the new config
        current_config = get_configuration()
        assert current_config.include_name is not None

    def test_none_configuration(self):
        """Test setting None as configuration (should work but not recommended)."""
        set_configuration(None)
        
        # get_configuration should still return a default Config
        config = get_configuration()
        assert isinstance(config, Config)
        assert config.include_name is None

    def test_configuration_with_lambda(self):
        """Test configuration with lambda function."""
        config = Config(include_name=lambda x: x in ['status', 'priority'])
        set_configuration(config)
        
        retrieved_config = get_configuration()
        assert retrieved_config.include_name('status') is True
        assert retrieved_config.include_name('priority') is True
        assert retrieved_config.include_name('other') is False

    def test_configuration_with_complex_filter(self):
        """Test configuration with more complex filter logic."""
        def complex_filter(name):
            # Include enums that end with '_status' or start with 'app_'
            return name.endswith('_status') or name.startswith('app_')
        
        config = Config(include_name=complex_filter)
        set_configuration(config)
        
        retrieved_config = get_configuration()
        assert retrieved_config.include_name('user_status') is True
        assert retrieved_config.include_name('app_priority') is True
        assert retrieved_config.include_name('order_type') is False
        assert retrieved_config.include_name('random_enum') is False