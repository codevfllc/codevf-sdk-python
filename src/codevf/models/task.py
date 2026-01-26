from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_UP
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .types import MetadataDict, JSONPrimitive


class ServiceMode(str, Enum):
    REALTIME_ANSWER = "realtime_answer"
    FAST = "fast"
    STANDARD = "standard"

    @property
    def sla_multiplier(self) -> Decimal:
        mapping = {
            ServiceMode.REALTIME_ANSWER: Decimal("2"),
            ServiceMode.FAST: Decimal("1.5"),
            ServiceMode.STANDARD: Decimal("1"),
        }
        return mapping[self]

    @classmethod
    def validate(cls, value: str) -> "ServiceMode":
        try:
            return cls(value)
        except ValueError as exc:
            raise ValueError(f"'{value}' is not a supported ServiceMode.") from exc


def calculate_final_credit_cost(
    max_credits: int, mode: ServiceMode, tag_multiplier: Decimal
) -> Decimal:
    raw = Decimal(max_credits) * mode.sla_multiplier * tag_multiplier
    return raw.quantize(Decimal("1"), rounding=ROUND_UP)


@dataclass(frozen=True)
class TaskDeliverable:
    file_name: str
    url: str
    uploaded_at: str
    mime_type: Optional[str] = None

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "TaskDeliverable":
        return cls(
            file_name=str(payload["fileName"]),
            url=str(payload["url"]),
            uploaded_at=str(payload["uploadedAt"]),
            mime_type=payload.get("mimeType"),
        )


@dataclass(frozen=True)
class TaskResult:
    message: Optional[str]
    deliverables: Sequence[TaskDeliverable]

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "TaskResult":
        items = payload.get("deliverables", [])
        if not isinstance(items, list):
            items = []
        deliverables = [TaskDeliverable.from_payload(item) for item in items]
        return cls(message=payload.get("message"), deliverables=deliverables)


@dataclass(frozen=True)
class TaskResponse:
    id: str
    status: str
    mode: ServiceMode
    max_credits: int
    created_at: str
    credits_used: Optional[int] = None
    result: Optional[TaskResult] = None

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "TaskResponse":
        mode_value = str(payload.get("mode", ServiceMode.STANDARD.value))
        mode = ServiceMode.validate(mode_value)
        result_payload = payload.get("result")
        result = TaskResult.from_payload(result_payload) if isinstance(result_payload, dict) else None
        return cls(
            id=str(payload["id"]),
            status=str(payload["status"]),
            mode=mode,
            max_credits=int(payload["maxCredits"]),
            created_at=str(payload["createdAt"]),
            credits_used=payload.get("creditsUsed"),
            result=result,
        )


@dataclass(frozen=True)
class TaskCreatePayload:
    prompt: str
    max_credits: int
    project_id: int
    mode: ServiceMode
    metadata: Optional[MetadataDict] = None
    tag_id: Optional[int] = None
    idempotency_key: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "prompt": self.prompt,
            "maxCredits": self.max_credits,
            "projectId": self.project_id,
            "mode": self.mode.value,
        }

        if self.metadata is not None:
            payload["metadata"] = dict(self.metadata)
        if self.tag_id is not None:
            payload["tagId"] = self.tag_id
        if self.idempotency_key is not None:
            payload["idempotencyKey"] = self.idempotency_key
        if self.attachments:
            payload["attachments"] = self.attachments

        return payload
