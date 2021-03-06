from typing import Mapping, Callable, Optional, List, Dict

from flask import current_app

from .domain import GithubEventActionType, GithubEvent, JiraEvent, \
    JiraEventType, JiraIssue, is_comment_event, is_update_event, \
    is_creation_event


# TODO: move to main app config.
DEFAULT_JIRA_ISSUETYPE = {'name': 'Task'}
DEFAULT_JIRA_PROJECT = {'key': 'ARXIVNG'}
DEFAULT_JIRA_ASSIGNEE = None
DEFAULT_JIRA_CLOSED_STATUS = {'id': '151'}
DEFAULT_JIRA_OPEN_STATUS = {'id': '161'}

GithubEventHandler = Callable[[GithubEvent], JiraEvent]


def translate(gh_event: GithubEvent, issue_key: Optional[str] = None,
                    comment_id: Optional[str] = None) -> Optional[JiraEvent]:
    if gh_event['event_type'] in event_translators:
        j_event = event_translators[gh_event['event_type']](gh_event)
        if issue_key is not None:
            if 'issue' not in j_event:
                j_event['issue'] = {}
            j_event['issue']['key'] = issue_key
        if comment_id is not None:
            if 'comment' not in j_event:
                j_event['comment'] = {}
            j_event['comment']['id'] = comment_id
        return j_event
    return None


def _make_description(gh_event: GithubEvent) -> str:
    return (f'GitHub user {gh_event["issue"]["user"]["login"]} writes'
            f' via {gh_event["issue"]["html_url"]} :'
            f'\n\n"{gh_event["issue"]["body"]}"')


def _make_comment_body(gh_event: GithubEvent) -> str:
    return (f'GitHub user {gh_event["comment"]["user"]["login"]} writes'
            f' via {gh_event["comment"]["html_url"]} :'
            f'\n\n"{gh_event["comment"]["body"]}"')

def _mark_edited(gh_event: GithubEvent, value: str) -> str:
    return (f'{value}\n\n'
            f' *(edited at {gh_event["issue"]["updated_at"].isoformat()}'
            f' by {gh_event["issue"]["user"]["login"]})*')


def _get_components(gh_event: GithubEvent) -> List[Dict[str, int]]:
    components_lookup = current_app.config['JIRA_COMPONENTS']
    component = components_lookup.get(gh_event['repository']['name'], None)
    if component is not None:
        return [{'id': component}]
    return []


def translate_issue_opened(gh_event: GithubEvent) -> JiraEvent:
    """Create a new Jira issue."""
    return {
        'event_type': JiraEventType.issue_create,
        'issue': {
            'project': DEFAULT_JIRA_PROJECT,
            'summary': gh_event["issue"]["title"],
            'description': _make_description(gh_event),
            'issuetype': DEFAULT_JIRA_ISSUETYPE,
            'assignee': DEFAULT_JIRA_ASSIGNEE,
            'components': _get_components(gh_event)
        }
    }


def translate_issue_edited(gh_event: GithubEvent) -> JiraEvent:
    """Edit an existing Jira issue."""
    return {
        'event_type': JiraEventType.issue_update,
        'issue': {
            'project': DEFAULT_JIRA_PROJECT,
            'summary': gh_event["issue"]["title"],
            'description': _mark_edited(gh_event, _make_description(gh_event)),
            'issuetype': DEFAULT_JIRA_ISSUETYPE,
            'assignee': DEFAULT_JIRA_ASSIGNEE
        }
    }


def translate_issue_closed(gh_event: GithubEvent) -> JiraEvent:
    """Close an existing Jira issue."""
    return {
        'event_type': JiraEventType.issue_transition,
        'issue': {
            'status': DEFAULT_JIRA_CLOSED_STATUS
        }
    }


def translate_issue_reopened(gh_event: GithubEvent) -> JiraEvent:
    """Reopen an existing Jira issue."""
    return {
        'event_type': JiraEventType.issue_transition,
        'issue': {
            'status': DEFAULT_JIRA_OPEN_STATUS
        }
    }


def translate_issue_deleted(gh_event: GithubEvent) -> JiraEvent:
    return {
        'event_type': JiraEventType.issue_transition,
        'issue': {
            'status': DEFAULT_JIRA_CLOSED_STATUS
        }
    }


def translate_comment_created(gh_event: GithubEvent) -> JiraEvent:
    return {
        'event_type': JiraEventType.comment_create,
        'comment': {
            'body': _make_comment_body(gh_event)
        }
    }

def translate_comment_deleted(gh_event: GithubEvent) -> JiraEvent:
    return {
        'event_type': JiraEventType.comment_delete,
        'comment': {}
    }


def translate_comment_edited(gh_event: GithubEvent) -> JiraEvent:
    return {
        'event_type': JiraEventType.comment_edit,
        'comment': {
            'body': _mark_edited(
                gh_event,
                f'Deleted at {gh_event["issue"]["updated_at"]}'
            )
        }
    }


event_translators: Mapping[GithubEventActionType, GithubEventHandler] = {
    GithubEventActionType.issue_opened: translate_issue_opened,
    GithubEventActionType.issue_edited: translate_issue_edited,
    GithubEventActionType.issue_closed: translate_issue_closed,
    GithubEventActionType.issue_deleted: translate_issue_deleted,
    GithubEventActionType.issue_reopened: translate_issue_reopened,
    GithubEventActionType.comment_created: translate_comment_created,
    GithubEventActionType.comment_deleted: translate_comment_deleted,
    GithubEventActionType.comment_edited: translate_comment_edited,
}