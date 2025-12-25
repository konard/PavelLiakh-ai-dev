import unittest
from unittest.mock import Mock

from src.app.ai_dev_workflow import AiDevWorkflow
from src.app.domain.story import Story, NEW_STATE
from src.infrastructure.github.issues_client import GithubIssue


class TestAiDevWorkflow(unittest.TestCase):
    def setUp(self):
        self.issues_client = Mock()
        self.story_service = Mock()
        self.development_service = Mock()
        self.log = Mock()

        self.workflow = AiDevWorkflow(
            self.issues_client, self.story_service, self.development_service, self.log
        )

    def test_run_ai_dev_workflow_calls_find_updates_and_process(self):
        self.issues_client.get_opened_issues.return_value = []
        self.story_service.get_new_stories.return_value = []

        self.workflow.run_ai_dev_workflow()

        self.issues_client.get_opened_issues.assert_called_once()
        self.story_service.get_new_stories.assert_called_once()

    def test_find_updates_processes_all_issues(self):
        issues = [
            GithubIssue(number=1, title="Issue 1", labels=["TODO"]),
            GithubIssue(number=2, title="Issue 2", labels=["bug"]),
            GithubIssue(number=3, title="Issue 3", labels=["TODO"]),
        ]
        self.issues_client.get_opened_issues.return_value = issues

        self.workflow._find_updates()

        assert self.story_service.check_for_update.call_count == 3

    def test_find_updates_with_no_issues(self):
        self.issues_client.get_opened_issues.return_value = []

        self.workflow._find_updates()

        self.story_service.check_for_update.assert_not_called()

    def test_process_implements_all_new_stories(self):
        stories = [
            Story(number=1, name="Story 1", state=NEW_STATE),
            Story(number=2, name="Story 2", state=NEW_STATE),
        ]
        self.story_service.get_new_stories.return_value = stories

        self.workflow._process()

        assert self.development_service.implement.call_count == 2
        self.development_service.implement.assert_any_call(stories[0])
        self.development_service.implement.assert_any_call(stories[1])

    def test_process_with_no_new_stories(self):
        self.story_service.get_new_stories.return_value = []

        self.workflow._process()

        self.development_service.implement.assert_not_called()

    def test_process_logs_story_count(self):
        stories = [Story(number=1, name="Story 1", state=NEW_STATE)]
        self.story_service.get_new_stories.return_value = stories

        self.workflow._process()

        log_calls = [call[0][0] for call in self.log.info.call_args_list]
        assert any("1 new stories" in call for call in log_calls)

    def test_find_updates_logs_issue_count(self):
        issues = [
            GithubIssue(number=1, title="Issue 1"),
            GithubIssue(number=2, title="Issue 2"),
        ]
        self.issues_client.get_opened_issues.return_value = issues

        self.workflow._find_updates()

        log_calls = [call[0][0] for call in self.log.info.call_args_list]
        assert any("2 open issues" in call for call in log_calls)


if __name__ == "__main__":
    unittest.main()
