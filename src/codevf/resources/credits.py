from typing import Any, Dict, cast

from ..models.credit import CreditBalance


class Credits:
    def __init__(self, client: Any) -> None:
        self._client = client

    def get_balance(self) -> CreditBalance:
        """
        Retrieve the current credit balance.

        Returns:
            A `CreditBalance` with available, on_hold, and total credits.
        """
        response = cast(Dict[str, Any], self._client.get("credits/balance"))
        return CreditBalance.from_payload(response)
