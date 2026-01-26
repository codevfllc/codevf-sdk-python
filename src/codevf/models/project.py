from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class Project:
    """Represents a CodeVF project resource."""

    id: int
    name: str
    created_at: str
    description: Optional[str] = None

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "Project":
        return cls(
            id=int(payload["id"]),
            name=str(payload["name"]),
            created_at=str(payload["createdAt"]),
            description=payload.get("description"),
        )
