import unittest
from unittest.mock import MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from codevf.resources.tasks import Tasks

class TestTasksValidation(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.tasks = Tasks(self.mock_client)

    def test_prompt_length_validation(self):
        # Too short
        with self.assertRaises(ValueError) as cm:
            self.tasks.create(prompt="short", max_credits=10, project_id=1)
        self.assertIn("Prompt must be between 10 and 10,000 characters", str(cm.exception))

        # Valid
        self.tasks.create(prompt="This is a valid prompt longer than 10 chars", max_credits=10, project_id=1)

    def test_max_credits_validation(self):
        # Too low
        with self.assertRaises(ValueError) as cm:
            self.tasks.create(prompt="Valid prompt", max_credits=0, project_id=1)
        self.assertIn("max_credits must be between 1 and 1920", str(cm.exception))

        # Too high
        with self.assertRaises(ValueError) as cm:
            self.tasks.create(prompt="Valid prompt", max_credits=1921, project_id=1)
        
        # Valid
        self.tasks.create(prompt="Valid prompt", max_credits=100, project_id=1)

    def test_mode_validation(self):
        with self.assertRaises(ValueError) as cm:
            self.tasks.create(prompt="Valid prompt", max_credits=10, project_id=1, mode="invalid")
        self.assertIn("Invalid mode", str(cm.exception))

        self.tasks.create(prompt="Valid prompt", max_credits=10, project_id=1, mode="fast")

    def test_attachments_validation(self):
        # Too many
        attachments = [{"fileName": "f.txt", "mimeType": "text/plain", "content": "c"}] * 6
        with self.assertRaises(ValueError) as cm:
            self.tasks.create(prompt="Valid prompt", max_credits=10, project_id=1, attachments=attachments)
        self.assertIn("Maximum of 5 attachments", str(cm.exception))

        # Missing fields
        attachments = [{"fileName": "f.txt"}] # Missing mimeType
        with self.assertRaises(ValueError) as cm:
            self.tasks.create(prompt="Valid prompt", max_credits=10, project_id=1, attachments=attachments)
        
        # Missing content/base64
        attachments = [{"fileName": "f.txt", "mimeType": "text/plain"}]
        with self.assertRaises(ValueError) as cm:
            self.tasks.create(prompt="Valid prompt", max_credits=10, project_id=1, attachments=attachments)

        # Valid content
        attachments = [{"fileName": "f.txt", "mimeType": "text/plain", "content": "text"}]
        self.tasks.create(prompt="Valid prompt", max_credits=10, project_id=1, attachments=attachments)

    def test_payload_construction(self):
        self.tasks.create(
            prompt="Valid prompt",
            max_credits=50,
            project_id=123,
            mode="fast",
            metadata={"key": "value"},
            idempotency_key="uuid",
            tag_id=99
        )
        
        # Check what was passed to client.post
        self.mock_client.post.assert_called_once()
        args, kwargs = self.mock_client.post.call_args
        self.assertEqual(args[0], "tasks/create")
        payload = kwargs['data']
        self.assertEqual(payload['prompt'], "Valid prompt")
        self.assertEqual(payload['maxCredits'], 50)
        self.assertEqual(payload['projectId'], 123)
        self.assertEqual(payload['mode'], "fast")
        self.assertEqual(payload['metadata'], {"key": "value"})
        self.assertEqual(payload['idempotencyKey'], "uuid")
        self.assertEqual(payload['tagId'], 99)

if __name__ == '__main__':
    unittest.main()
