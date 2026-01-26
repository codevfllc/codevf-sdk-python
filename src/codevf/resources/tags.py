from __future__ import annotations

from typing import Any, Dict, List, cast

from ..models.tag import Tag


class Tags:
    def __init__(self, client: Any) -> None:
        self._client = client

    def list(self) -> List[Tag]:
        """
        Retrieve available engineer expertise levels (tags).
        """
        response = cast(Dict[str, Any], self._client.get("tags"))
        tags_payload = response.get("tags", [])
        if not isinstance(tags_payload, list):
            return []

        return [
            Tag.from_payload(tag)
            for tag in tags_payload
            if isinstance(tag, dict)
        ]
