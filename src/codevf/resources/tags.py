from typing import Dict, Any, List, cast

class Tags:
    """
    Resource class for managing Tags (engineer expertise levels).
    """
    def __init__(self, client: Any) -> None:
        self._client = client

    def list(self) -> List[Dict[str, Any]]:
        """
        Retrieve available engineer expertise levels along with their cost multipliers 
        and related metadata.
        
        This method sends a GET request to the /tags endpoint. Each tag represents 
        a different level of engineer expertise. The selected tag affects the final 
        credit cost of a task.
        
        The tagId returned by this method can be used in task creation (Tasks.create) 
        to select the desired engineer expertise level.
        
        The final credit calculation follows this formula:
        final credits = base credits × SLA multiplier × tag multiplier

        Returns:
            A list of tag objects, each containing:
            - 'id' (int): Unique identifier for the tag. Use this as 'tag_id' in Tasks.create.
            - 'name' (str): Short name of the expertise level (e.g., 'standard', 'expert').
            - 'displayName' (str): Human-readable label for the expertise level.
            - 'description' (str): Detailed explanation of what this level provides.
            - 'costMultiplier' (float): The multiplier applied to the base cost.
            - 'isActive' (bool): Whether this tag is currently available for new tasks.
            - 'sortOrder' (int): Numeric value for sorting tags in a UI.

        Raises:
            APIError: If the API request fails.
        """
        response = self._client.get("tags")
        
        # If the API returns { "success": True, "data": [...] }
        if isinstance(response, dict) and "data" in response:
            return cast(List[Dict[str, Any]], response["data"])
        
        # Fallback if the API returns the list directly
        return cast(List[Dict[str, Any]], response)