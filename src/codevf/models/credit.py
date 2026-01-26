from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping


@dataclass(frozen=True)
class CreditBalance:
    available: Decimal
    on_hold: Decimal
    total: Decimal

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "CreditBalance":
        return cls(
            available=Decimal(str(payload["available"])),
            on_hold=Decimal(str(payload["onHold"])),
            total=Decimal(str(payload["total"])),
        )
