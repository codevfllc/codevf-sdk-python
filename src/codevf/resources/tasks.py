from __future__ import annotations

import uuid
from typing import Any, Dict, Mapping, Optional, Sequence, cast

from ..exceptions import (
    AttachmentLimitExceededError,
    InvalidModeError,
    InvalidTagError,
)
from ..models.attachment import normalize_attachments
from ..models.task import ServiceMode, TaskCreatePayload, TaskResponse
from ..models.types import MetadataDict
from ..utils.metadata import validate_metadata


PROMPT_MIN_LENGTH = 10
PROMPT_MAX_LENGTH = 10_000
MIN_CREDITS = 1
MAX_CREDITS = 1920
MAX_ATTACHMENTS = 5


class Tasks:
    def __init__(self, client: Any) -> None:
        self._client = client

    def create(
        self,
        prompt: str,
        max_credits: int,
        project_id: int,
        *,
        mode: ServiceMode | str = ServiceMode.STANDARD,
        metadata: Optional[MetadataDict] = None,
        idempotency_key: Optional[str] = None,
        attachments: Optional[Sequence[Mapping[str, Any]]] = None,
        tag_id: Optional[int] = None,
    ) -> TaskResponse:
        """
        Submit a new task request.

        Args:
            prompt: A descriptive request between 10 and 10,000 characters.
            max_credits: The upper bound on credits to spend (1-1,920).
            project_id: The integer ID returned from `Projects.create`.
            mode: Service level: realtime_answer, fast, or standard.
            metadata: Flat metadata dictionary for future filtering.
            idempotency_key: Optional UUID v4 to deduplicate submissions.
            attachments: File attachments (JSON-compatible dicts).
            tag_id: Expert-level tag ID to control cost multiplier.

        Returns:
            A `TaskResponse` wrapping the server payload.
        """
        self._validate_prompt(prompt)
        self._validate_max_credits(max_credits)
        mode_enum = self._resolve_mode(mode)

        normalized_meta = validate_metadata(metadata)

        if attachments and len(attachments) > MAX_ATTACHMENTS:
            raise AttachmentLimitExceededError("Maximum of five attachments allowed.")
        normalized_attachments = normalize_attachments(attachments)

        if idempotency_key is not None:
            self._validate_idempotency_key(idempotency_key)

        if tag_id is not None and tag_id <= 0:
            raise InvalidTagError("tag_id must be a positive integer.")

        payload = TaskCreatePayload(
            prompt=prompt,
            max_credits=max_credits,
            project_id=project_id,
            mode=mode_enum,
            metadata=normalized_meta,
            tag_id=tag_id,
            idempotency_key=idempotency_key,
            attachments=normalized_attachments or None,
        )

        response = cast(Dict[str, Any], self._client.post("tasks/create", data=payload.to_dict()))
        return TaskResponse.from_payload(response)

    def retrieve(self, task_id: str) -> TaskResponse:
        """Fetch the latest task status and deliverables."""
        if not task_id:
            raise ValueError("task_id must be provided.")

        response = cast(Dict[str, Any], self._client.get(f"tasks/{task_id}"))
        return TaskResponse.from_payload(response)

    def cancel(self, task_id: str) -> Dict[str, Any]:
        """Cancel a pending or in-progress task."""
        if not task_id:
            raise ValueError("task_id must be provided.")

        return cast(Dict[str, Any], self._client.post(f"tasks/{task_id}/cancel"))

    def _resolve_mode(self, mode: ServiceMode | str) -> ServiceMode:
        if isinstance(mode, ServiceMode):
            return mode
        try:
            return ServiceMode.validate(str(mode))
        except ValueError as exc:
            raise InvalidModeError(str(exc)) from exc

    def _validate_prompt(self, prompt: str) -> None:
        length = len(prompt)
        if length < PROMPT_MIN_LENGTH or length > PROMPT_MAX_LENGTH:
            raise ValueError("prompt must be between 10 and 10,000 characters.")

    def _validate_max_credits(self, max_credits: int) -> None:
        if max_credits < MIN_CREDITS or max_credits > MAX_CREDITS:
            raise ValueError("max_credits must be between 1 and 1,920.")

    def _validate_idempotency_key(self, key: str) -> None:
        try:
            uuid.UUID(key)
        except ValueError as exc:
            raise ValueError("idempotency_key must be a valid UUID.") from exc
