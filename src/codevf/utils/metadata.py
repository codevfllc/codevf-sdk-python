from __future__ import annotations

from typing import Dict, Mapping, Optional

from ..exceptions import InvalidMetadataError
from ..models.types import JSONPrimitive, MetadataDict

def validate_metadata(metadata: Optional[MetadataDict]) -> Optional[Dict[str, JSONPrimitive]]:
    if metadata is None:
        return None

    if not isinstance(metadata, Mapping):
        raise InvalidMetadataError("Metadata must be a mapping with string keys.")

    validated: Dict[str, JSONPrimitive] = {}
    for key, value in metadata.items():
        if not isinstance(key, str):
            raise InvalidMetadataError("Metadata keys must be strings.")
        if value is not None and not isinstance(value, (str, bool, int, float)):
            raise InvalidMetadataError("Metadata values must be strings, numbers, booleans, or null.")
        validated[key] = value

    return validated
