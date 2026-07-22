import unittest
from unittest.mock import Mock, patch

from test_api import run_test


class SmokeTestRunnerTests(unittest.TestCase):
    @patch("test_api.requests.get")
    @patch("test_api.requests.post")
    def test_run_test_returns_true_for_completed_job(self, post, get):
        post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"id": "job-1"}),
        )
        get.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"status": "COMPLETED", "output": {}}),
        )

        passed = run_test(
            "https://api.runpod.ai/v2/endpoint",
            {"Authorization": "Bearer token"},
            "chat",
            {"input": {"messages": []}},
            timeout=10,
            poll_interval=0,
            request_timeout=3,
        )

        self.assertTrue(passed)
        self.assertEqual(post.call_args.kwargs["timeout"], 3)
        self.assertEqual(get.call_args.kwargs["timeout"], 3)

    @patch("test_api.requests.post")
    def test_run_test_returns_false_when_deadline_is_exhausted(self, post):
        post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"id": "job-2"}),
        )

        passed = run_test(
            "https://api.runpod.ai/v2/endpoint",
            {},
            "chat",
            {"input": {"messages": []}},
            timeout=0,
            poll_interval=0,
            request_timeout=3,
        )

        self.assertFalse(passed)


if __name__ == "__main__":
    unittest.main()
