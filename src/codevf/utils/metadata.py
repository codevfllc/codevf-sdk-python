from __future__ import annotations

import re
from typing import Dict, Mapping, Optional

from ..exceptions import InvalidMetadataError
from ..models.types import JSONPrimitive, MetadataDict

METADATA_KEY_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")


def validate_metadata(metadata: Optional[MetadataDict]) -> Optional[Dict[str, JSONPrimitive]]:
    if metadata is None:
        return None

    if not isinstance(metadata, Mapping):
        raise InvalidMetadataError("Metadata must be a mapping with string keys.")

    validated: Dict[str, JSONPrimitive] = {}
    for key, value in metadata.items():
        if not isinstance(key, str) or not METADATA_KEY_PATTERN.fullmatch(key):
            raise InvalidMetadataError("Metadata keys must be alphanumeric with optional underscores.")
        if not isinstance(value, (str, bool, int, float)):
            raise InvalidMetadataError("Metadata values must be strings, numbers, or booleans.")
        validated[key] = value

    return validated
