from typing import Any

class Credits:
    def __init__(self, client):
        self._client = client

    def retrieve_balance(self) -> Any:
        """
        Retrieve the current credit balance.
        
        Returns:
            The credit balance information.
        """
        return self._client.get("credits/balance")
