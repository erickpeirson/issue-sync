
import json
from unittest import TestCase, mock

from sync import process
from sync.parse import parse_github_event
from sync import domain


class TestIssuesEventEdited(TestCase):
    """Received an IssuesEvent with action ``edited``."""

    EXAMPLE = 'tests/data/github/issuesevent/edited.json'

    def setUp(self):
        """Load sample payload."""
        with open(self.EXAMPLE) as f:
            self.data = json.load(f)
        self.event = parse_github_event(domain.GithubEventType.IssuesEvent,
                                        self.data)

    def test_translate_event(self):
        """Translate the Github event."""
        issue_key = 'ARXIVNG-1234'
        jira_event = process.translate_event(self.event, issue_key=issue_key)
        self.assertIsNotNone(jira_event, 'Triggers a Jira event')
        self.assertEqual(jira_event['event_type'],
                         domain.JiraEventType.issue_update,
                         'Updates Jira issue')
        self.assertEqual(jira_event['issue']['key'], issue_key,
                         'Uses provided issue key')








