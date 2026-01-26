from __future__ import annotations

import base64
import binascii
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from ..exceptions import AttachmentTooLargeError

MAX_TEXT_BYTES = 1_048_576
MAX_BINARY_BYTES = 10_485_760
ATTACHMENT_LIMIT = 5


@dataclass(frozen=True)
class AttachmentCategory:
    name: str
    extensions: Tuple[str, ...]
    mime_types: Tuple[str, ...]
    max_bytes: int
    requires_base64: bool

    def matches(self, file_name: str, mime_type: str) -> bool:
        lower_name = file_name.lower()
        if any(lower_name.endswith(f".{ext}") for ext in self.extensions if ext):
            return True
        if mime_type in self.mime_types:
            return True
        return False


IMAGE_CATEGORY = AttachmentCategory(
    name="image",
    extensions=("png", "jpg", "jpeg", "gif", "webp"),
    mime_types=("image/png", "image/jpeg", "image/gif", "image/webp"),
    max_bytes=MAX_BINARY_BYTES,
    requires_base64=True,
)

PDF_CATEGORY = AttachmentCategory(
    name="pdf",
    extensions=("pdf",),
    mime_types=("application/pdf",),
    max_bytes=MAX_BINARY_BYTES,
    requires_base64=True,
)

CODE_CATEGORY = AttachmentCategory(
    name="code",
    extensions=("py", "js", "ts", "java", "cpp", "c", "cs", "go", "rs", "kt", "swift", "php", "rb", "jsx", "tsx"),
    mime_types=(
        "text/x-python",
        "application/javascript",
        "text/typescript",
        "text/x-java-source",
        "text/plain",
        "application/x-c++src",
        "text/x-csrc",
        "text/x-csharp",
        "text/x-go",
        "text/x-rustsrc",
        "text/x-kotlin",
        "text/x-php",
        "text/x-ruby",
    ),
    max_bytes=MAX_TEXT_BYTES,
    requires_base64=False,
)

TEXT_CATEGORY = AttachmentCategory(
    name="text",
    extensions=("txt", "json", "xml", "csv", "log"),
    mime_types=("text/plain", "application/json", "text/xml", "application/xml", "text/csv"),
    max_bytes=MAX_TEXT_BYTES,
    requires_base64=False,
)

ALL_CATEGORIES: Tuple[AttachmentCategory, ...] = (
    IMAGE_CATEGORY,
    PDF_CATEGORY,
    CODE_CATEGORY,
    TEXT_CATEGORY,
)


class Attachment:
    """Represents a validated attachment ready for the CodeVF API."""

    def __init__(self, file_name: str, mime_type: str, content: str, category: AttachmentCategory):
        if not file_name:
            raise AttachmentTooLargeError("fileName cannot be empty.")
        if not mime_type:
            raise AttachmentTooLargeError("mimeType cannot be empty.")

        self.file_name = file_name
        self.mime_type = mime_type
        self.content = content
        self.category = category
        self._validate_content()

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "Attachment":
        if not isinstance(raw, Mapping):
            raise AttachmentTooLargeError("Each attachment must be a mapping.")

        file_name = raw.get("fileName") or raw.get("file_name")
        mime_type = raw.get("mimeType") or raw.get("mime_type")
        content = raw.get("content")
        if "base64" in raw and content is None:
            content = raw["base64"]

        if not isinstance(content, str):
            raise AttachmentTooLargeError("content/base64 must be a string.")

        if not isinstance(file_name, str) or not isinstance(mime_type, str):
            raise AttachmentTooLargeError("fileName and mimeType must be strings.")

        category = cls._select_category(file_name, mime_type)
        return cls(file_name=file_name, mime_type=mime_type, content=content, category=category)

    @staticmethod
    def _select_category(file_name: str, mime_type: str) -> AttachmentCategory:
        for category in ALL_CATEGORIES:
            if category.matches(file_name, mime_type):
                return category
        lower_name = file_name.lower()
        if lower_name.endswith(".pdf"):
            return PDF_CATEGORY
        if lower_name.endswith(".txt") or lower_name.endswith(".log"):
            return TEXT_CATEGORY
        raise AttachmentTooLargeError(
            f"Unsupported attachment type: '{file_name}' ({mime_type})."
        )

    @staticmethod
    def _calculate_bytes(content: str, requires_base64: bool) -> int:
        if requires_base64:
            cleaned = re.sub(r"\s+", "", content)
            return len(cleaned.encode("utf-8"))
        return len(content.encode("utf-8"))

    def _validate_content(self) -> None:
        size = self._calculate_bytes(self.content, self.category.requires_base64)
        if size > self.category.max_bytes:
            raise AttachmentTooLargeError(
                f"{self.file_name} exceeds the {self.category.max_bytes} byte limit for {self.category.name} files."
            )

        if self.category.requires_base64:
            try:
                base64.b64decode(self.content, validate=True)
            except (ValueError, binascii.Error):
                raise AttachmentTooLargeError(
                    f"{self.file_name} must be valid base64 when uploading {self.category.name} files."
                )

    def to_payload(self) -> Dict[str, str]:
        return {"fileName": self.file_name, "mimeType": self.mime_type, "content": self.content}


def normalize_attachments(
    attachments: Optional[Iterable[Mapping[str, Any]]]
) -> List[Dict[str, str]]:
    if attachments is None:
        return []

    payloads: List[Dict[str, str]] = []
    for mapping in attachments:
        attachment = Attachment.from_mapping(mapping)
        payloads.append(attachment.to_payload())

    return payloads
