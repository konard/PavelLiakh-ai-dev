import unittest
from unittest.mock import Mock, MagicMock, patch
from src.infrastructure.github.issues_client import IssuesClient, GithubIssue


class TestIssuesClient(unittest.TestCase):
    def setUp(self):
        self.log = Mock()

    @patch('src.infrastructure.github.issues_client.Github')
    @patch('src.infrastructure.github.issues_client.config')
    def test_get_opened_issues_fetches_all_pages(self, mock_config, mock_github_class):
        mock_config.github_api_key = "test_key"
        mock_config.github_repo_name = "test/repo"

        mock_issue1 = Mock()
        mock_issue1.number = 1
        mock_issue1.title = "Issue 1"
        mock_issue1.body = "Body 1"
        mock_issue1.labels = []

        mock_issue2 = Mock()
        mock_issue2.number = 2
        mock_issue2.title = "Issue 2"
        mock_issue2.body = "Body 2"
        mock_issue2.labels = []

        mock_issue3 = Mock()
        mock_issue3.number = 3
        mock_issue3.title = "Issue 3"
        mock_issue3.body = "Body 3"
        mock_issue3.labels = []

        mock_paginated_list = MagicMock()
        mock_paginated_list.__iter__ = Mock(return_value=iter([mock_issue1, mock_issue2, mock_issue3]))

        mock_repo = Mock()
        mock_repo.get_issues = Mock(return_value=mock_paginated_list)

        mock_github = Mock()
        mock_github.get_repo = Mock(return_value=mock_repo)
        mock_github_class.return_value = mock_github

        client = IssuesClient(self.log)
        issues = client.get_opened_issues()

        self.assertEqual(3, len(issues))
        self.assertEqual(1, issues[0].number)
        self.assertEqual("Issue 1", issues[0].title)
        self.assertEqual(2, issues[1].number)
        self.assertEqual("Issue 2", issues[1].title)
        self.assertEqual(3, issues[2].number)
        self.assertEqual("Issue 3", issues[2].title)

    @patch('src.infrastructure.github.issues_client.Github')
    @patch('src.infrastructure.github.issues_client.config')
    def test_get_opened_issues_handles_empty_body(self, mock_config, mock_github_class):
        mock_config.github_api_key = "test_key"
        mock_config.github_repo_name = "test/repo"

        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.title = "Issue without body"
        mock_issue.body = None
        mock_issue.labels = []

        mock_paginated_list = MagicMock()
        mock_paginated_list.__iter__ = Mock(return_value=iter([mock_issue]))

        mock_repo = Mock()
        mock_repo.get_issues = Mock(return_value=mock_paginated_list)

        mock_github = Mock()
        mock_github.get_repo = Mock(return_value=mock_repo)
        mock_github_class.return_value = mock_github

        client = IssuesClient(self.log)
        issues = client.get_opened_issues()

        self.assertEqual(1, len(issues))
        self.assertEqual("", issues[0].body)


if __name__ == "__main__":
    unittest.main()
