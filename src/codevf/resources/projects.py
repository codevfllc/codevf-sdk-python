from typing import Dict, Any, Optional, cast

class Projects:
    def __init__(self, client: Any) -> None:
        self._client = client

    def create(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new project.

        Args:
            name: The name of the project (required, unique per user).
            description: An optional description for the project.

        Returns:
            The created project data containing 'id', 'name', and 'createdAt'.
        """
        payload = {"name": name}
        if description is not None:
            payload["description"] = description
            
        return cast(Dict[str, Any], self._client.post("projects/create", data=payload))
