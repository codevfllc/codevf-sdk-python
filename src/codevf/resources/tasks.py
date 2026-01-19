from typing import Dict, Any, List, Optional, Union

class Tasks:
    def __init__(self, client):
        self._client = client

    def create(
        self,
        prompt: str,
        max_credits: int,
        project_id: int,
        mode: str = "standard",
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        tag_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a new task.

        Args:
            prompt: Task description (10-10,000 chars).
            max_credits: Maximum credits to allocate (1-1920).
            project_id: ID of the project to associate the task with.
            mode: Task mode ('realtime_answer', 'fast', 'standard'). Defaults to 'standard'.
            metadata: Optional dictionary for user reference.
            idempotency_key: Optional UUID string to ensure idempotency.
            attachments: Optional list of file attachments (max 5).
                         Each attachment must be a dict with:
                         - 'fileName': str
                         - 'mimeType': str
                         - 'base64': str (optional)
                         - 'content': str (optional, for raw text)
            tag_id: Optional ID indicating engineer expertise level.

        Returns:
            The created task data containing 'id', 'status', 'mode', 'maxCredits', 'createdAt'.

        Raises:
            ValueError: If input parameters violate constraints.
            APIError: If the API request fails.
        """
        # Validate prompt
        if not (10 <= len(prompt) <= 10000):
            raise ValueError("Prompt must be between 10 and 10,000 characters.")

        # Validate max_credits
        if not (1 <= max_credits <= 1920):
            raise ValueError("max_credits must be between 1 and 1920.")

        # Validate mode
        valid_modes = {"realtime_answer", "fast", "standard"}
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of {valid_modes}.")

        # Validate attachments
        if attachments:
            if len(attachments) > 5:
                raise ValueError("Maximum of 5 attachments allowed.")
            
            for i, att in enumerate(attachments):
                if not isinstance(att, dict):
                    raise ValueError(f"Attachment at index {i} must be a dictionary.")
                if "fileName" not in att or "mimeType" not in att:
                    raise ValueError(f"Attachment at index {i} missing required fields 'fileName' or 'mimeType'.")
                if "base64" not in att and "content" not in att:
                    raise ValueError(f"Attachment at index {i} must provide either 'base64' or 'content'.")

        payload = {
            "prompt": prompt,
            "maxCredits": max_credits,
            "projectId": project_id,
            "mode": mode,
        }

        if metadata is not None:
            payload["metadata"] = metadata
        
        if idempotency_key is not None:
            payload["idempotencyKey"] = idempotency_key
            
        if attachments is not None:
            payload["attachments"] = attachments
            
        if tag_id is not None:
            payload["tagId"] = tag_id

        return self._client.post("tasks/create", data=payload)

    def retrieve(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieve a task by ID to check its status and results.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            A dictionary containing the task data. 
            The response includes:
            - 'id': The task ID.
            - 'status': One of 'pending', 'processing', 'completed', or 'cancelled'.
            
            When status is 'completed', it also includes:
            - 'creditsUsed': Total credits consumed by the task.
            - 'result': A dictionary containing:
                - 'message': Summary of the task completion.
                - 'deliverables': A list of dictionaries, each with:
                    - 'fileName': Name of the produced file.
                    - 'url': Link to download the file.
                    - 'uploadedAt': Timestamp of when the file was uploaded.

        Raises:
            ValueError: If task_id is empty.
            APIError: If the API request fails (e.g., 404 Not Found).
        """
        if not task_id:
            raise ValueError("task_id must be provided.")
            
        return self._client.get(f"tasks/{task_id}")

    def cancel(self, task_id: str) -> Dict[str, Any]:
        """
        Cancel a task by ID.
        
        Args:
            task_id: The ID of the task to cancel.
        
        Returns:
            A dictionary containing the cancellation confirmation.
            Example:
            {
                "message": "Task cancelled successfully.",
                "creditsReturned": 12
            }
            
        Raises:
            ValueError: If task_id is empty.
            APIError: If the cancellation fails.
        """
        if not task_id:
            raise ValueError("task_id must be provided.")
            
        return self._client.post(f"tasks/{task_id}/cancel")
