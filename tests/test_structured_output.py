import pytest
from codevf.models.task import TaskResponse, TaskResult, ServiceMode

def test_parse_standard_result():
    """Verify that standard results (message + deliverables) parse into TaskResult."""
    payload = {
        "id": "task_1",
        "status": "completed",
        "mode": "standard",
        "maxCredits": 240,
        "createdAt": "2026-01-01T00:00:00Z",
        "result": {
            "message": "Standard analysis",
            "deliverables": []
        }
    }
    task = TaskResponse.from_payload(payload)
    assert isinstance(task.result, TaskResult)
    assert task.result.message == "Standard analysis"
    assert task.response_schema is None

def test_parse_structured_result_with_schema_discriminator():
    """
    Verify that if responseSchema is present, the result is returned as a raw dict
    even if it contains 'message' and 'deliverables' keys.
    """
    schema = {"type": "object", "properties": {"message": {"type": "string"}}}
    payload = {
        "id": "task_2",
        "status": "completed",
        "mode": "realtime_answer",
        "maxCredits": 60,
        "createdAt": "2026-01-01T00:00:00Z",
        "responseSchema": schema,
        "result": {
            "message": "Structured message",
            "deliverables": "This is NOT a list, but schema allows it as a string maybe"
        }
    }
    task = TaskResponse.from_payload(payload)
    # It MUST be a dict because responseSchema was provided
    assert isinstance(task.result, dict)
    assert task.result["message"] == "Structured message"
    assert task.response_schema == schema

def test_parse_structured_result_fallback():
    """
    Verify that if responseSchema is NOT present but the shape doesn't match 
    standard TaskResult, it still returns a raw dict.
    """
    payload = {
        "id": "task_3",
        "status": "completed",
        "mode": "realtime_answer",
        "maxCredits": 60,
        "createdAt": "2026-01-01T00:00:00Z",
        "result": {
            "score": 95,
            "issues": []
        }
    }
    task = TaskResponse.from_payload(payload)
    assert isinstance(task.result, dict)
    assert task.result["score"] == 95
