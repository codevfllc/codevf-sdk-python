from typing import Dict, Any

class Projects:
    def __init__(self, client):
        self._client = client

    def create(self, params: Dict[str, Any]) -> Any:
        """
        Create a new project.
        
        Args:
            params: Dictionary containing project creation parameters.
        
        Returns:
            The created project data.
        """
        return self._client.post("projects/create", data=params)
