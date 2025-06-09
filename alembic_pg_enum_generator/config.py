from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class Config:
    include_name: Optional[Callable[[str, str], bool]] = None


_configuration: Optional[Config] = None


def get_configuration() -> Config:
    global _configuration
    if _configuration is None:
        _configuration = Config()
    return _configuration


def set_configuration(configuration: Config) -> None:
    global _configuration
    _configuration = configuration