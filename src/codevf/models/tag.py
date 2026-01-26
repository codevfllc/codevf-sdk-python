from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class Tag:
    """Metadata for an engineer expertise level."""

    id: int
    name: str
    display_name: str
    description: Optional[str]
    cost_multiplier: Decimal
    is_active: bool
    sort_order: int
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    is_deprecated: Optional[bool] = None

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "Tag":
        multiplier_raw = payload.get("costMultiplier", "1.0")
        return cls(
            id=int(payload["id"]),
            name=str(payload["name"]),
            display_name=str(payload["displayName"]),
            description=payload.get("description"),
            cost_multiplier=Decimal(str(multiplier_raw)),
            is_active=bool(payload.get("isActive", False)),
            sort_order=int(payload.get("sortOrder", 0)),
            valid_from=payload.get("validFrom"),
            valid_to=payload.get("validTo"),
            is_deprecated=payload.get("isDeprecated"),
        )
