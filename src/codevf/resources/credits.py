from typing import Dict, Any

class Credits:
    def __init__(self, client: Any) -> None:
        self._client = client

    def get_balance(self) -> Dict[str, Any]:
        """
        Retrieve the current credit balance.
        
        Returns:
            A dictionary containing:
                - 'available' (float): Credits available for use.
                - 'onHold' (float): Credits currently held for active tasks.
                - 'total' (float): Total credits (available + onHold).

        Raises:
            APIError: If the API request fails.
        """
        return self._client.get("credits/balance")

    def retrieve_balance(self) -> Dict[str, Any]:
        """
        Retrieve the current credit balance. Alias for get_balance().
        
        Returns:
            The credit balance information.
        """
        return self.get_balance()
