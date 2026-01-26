from typing import Any, Dict, Optional, cast

from ..models.project import Project


class Projects:
    def __init__(self, client: Any) -> None:
        self._client = client

    def create(self, name: str, description: Optional[str] = None) -> Project:
        """
        Create or reuse a project with the given name.

        The API will return an existing project if one with the same name already exists,
        so calling `create` repeatedly is idempotent from the caller's perspective.
        """
        payload: Dict[str, Any] = {"name": name}
        if description is not None:
            payload["description"] = description

        response = cast(Dict[str, Any], self._client.post("projects/create", data=payload))
        return Project.from_payload(response)
