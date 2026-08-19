__version__ = "0.1.0"

from .normalizer import normalize_record
from .schema import NormalizedEvent, SCHEMA_VERSION

__all__ = [
    "NormalizedEvent",
    "SCHEMA_VERSION",
    "normalize_record",
]
