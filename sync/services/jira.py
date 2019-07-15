
from flask import Flask, g, current_app
from jira import JIRA

from ..domain import JiraEvent, JiraEventType


class PropagationFailed(Exception):
    """Propagation of the event to Jira failed."""


class JiraService:
    def __init__(self, endpoint: str, username: str, token: str) -> None:
        self._endpoint = endpoint
        self._username = username
        self._token = token
        self._jira = self._new_connection(self._endpoint, self._username,
                                          self._token)

    @staticmethod
    def _new_connection(endpoint: str, username: str, token: str) -> JIRA:
        return JIRA(endpoint, basic_auth=(username, token))

    def create_ticket(self, event: JiraEvent) -> JiraEvent:
        ticket = self._jira.create_issue(**event['issue'])
        event['issue']['key'] = ticket.key
        return event

    def update_ticket(self, event: JiraEvent) -> JiraEvent:
        issue_key = event['issue'].get('key')
        if issue_key is None:
            raise PropagationFailed('Missing issue key')
        issue = self._jira.issue(issue_key)
        issue.update(**{k: v for k, v in event['issue'].items() if k != 'key'})
        return event

    def transition_ticket(self, event: JiraEvent) -> None:
        issue_key = event['issue'].get('key')
        if issue_key is None:
            raise PropagationFailed('Missing issue key')
        issue = self._jira.issue(issue_key)
        self._jira.transition_issue(issue, event['issue']['status']['id'])
        return event

    def create_comment(self, event: JiraEvent) -> JiraEvent:
        issue_key = event['issue'].get('key')
        if issue_key is None:
            raise PropagationFailed('Missing issue key')
        comment = self._jira.add_comment(issue_key, event['comment']['body'])
        event['comment']['id'] = comment.id
        return event

    def update_comment(self, event: JiraEvent) -> JiraEvent:
        issue_key = event['issue'].get('key')
        if issue_key is None:
            raise PropagationFailed('Missing issue key')
        comment_id = event['comment'].get('id')
        if comment_id is None:
            raise PropagationFailed('Missing comment id')
        comment = self._jira.comment(issue_key, comment_id)
        comment.update(body=event['comment']['body'])
        return event

    def delete_comment(self, event: JiraEvent) -> JiraEvent:
        issue_key = event['issue'].get('key')
        if issue_key is None:
            raise PropagationFailed('Missing issue key')
        comment_id = event['comment'].get('id')
        if comment_id is None:
            raise PropagationFailed('Missing comment id')
        comment = self._jira.comment(issue_key, comment_id)
        comment.delete()
        return event



def propagate(jira_event: JiraEvent) -> JiraEvent:
    current_app.logger.debug('Propagate Jira event: %s',
                             jira_event['event_type'].name)
    if 'jira' not in g:
        config = current_app.config
        g.jira = JiraService(config['JIRA_ENDPOINT'], config['JIRA_USERNAME'],
                             config['JIRA_TOKEN'])
    handler = handlers.get(jira_event['event_type'])
    if handler is None:
        current_app.logger.info('Nothing to do for %s', jira_event['event_type'])
        return jira_event    # Nothing to do.
    try:
        return getattr(g.jira, handler.__name__)(jira_event)
    except KeyError as e:
        raise PropagationFailed('Missing data') from e


def init_app(app: Flask) -> None:
    pass


handlers = {
    JiraEventType.issue_create: JiraService.create_ticket,
    JiraEventType.issue_update: JiraService.update_ticket,
    JiraEventType.issue_transition: JiraService.transition_ticket,
    JiraEventType.comment_create: JiraService.create_comment,
    JiraEventType.comment_edit: JiraService.update_comment,
    JiraEventType.comment_delete: JiraService.delete_comment,
}