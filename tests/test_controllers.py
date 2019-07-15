
import json
from unittest import TestCase, mock

from sync import controllers
from sync.parse import parse_github_event
from sync import domain


class TestIssuesEventEdited(TestCase):
    """Received an IssuesEvent with action ``edited``."""

    EXAMPLE = 'tests/data/github/issuesevent/edited.json'

    def setUp(self):
        """Load sample payload."""
        with open(self.EXAMPLE) as f:
            self.data = json.load(f)

    @mock.patch(f'{controllers.__name__}.current_app', mock.MagicMock())
    @mock.patch(f'{controllers.__name__}.database')
    @mock.patch(f'{controllers.__name__}.jira')
    def test_handle_event(self, mock_jira, mock_database):
        """Handle the Github event."""
        mock_jira.propagate.side_effect = lambda o: o
        data, code, headers = controllers.handle_issuesevent(self.data)

        jira_event, = mock_jira.propagate.call_args[0]

        self.assertIsNotNone(jira_event, 'Triggers a Jira event')
        self.assertEqual(jira_event['event_type'],
                         domain.JiraEventType.issue_update,
                         'Updates Jira issue')
        self.assertEqual(jira_event['issue']['key'],
                         mock_database.get_jira_issue_key.return_value,
                         'Uses issue key retrieved from database')