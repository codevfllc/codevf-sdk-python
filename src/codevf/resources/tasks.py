from typing import Dict, Any

class Tasks:
    def __init__(self, client):
        self._client = client

    def create(self, params: Dict[str, Any]) -> Any:
        """
        Create a new task.
        
        Args:
            params: Dictionary containing task creation parameters.
        
        Returns:
            The created task data.
        """
        return self._client.post("tasks/create", data=params)

    def retrieve(self, task_id: str) -> Any:
        """
        Retrieve a task by ID.
        
        Args:
            task_id: The ID of the task to retrieve.
        
        Returns:
            The task data.
        """
        return self._client.get(f"tasks/{task_id}")

    def cancel(self, task_id: str) -> Any:
        """
        Cancel a task by ID.
        
        Args:
            task_id: The ID of the task to cancel.
        
        Returns:
            The result of the cancellation request.
        """
        return self._client.post(f"tasks/{task_id}/cancel")
