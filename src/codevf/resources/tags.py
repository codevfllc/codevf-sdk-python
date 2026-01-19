from typing import Any

class Tags:
    def __init__(self, client):
        self._client = client

    def list(self) -> Any:
        """
        List all available tags.
        
        Returns:
            A list of tags.
        """
        return self._client.get("tags")
