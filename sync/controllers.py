from typing import Optional
from pprint import pprint
from http import HTTPStatus

from . import domain
from .parse import parse_github_event
from .services import database, jira
from .process import translate_event


def handle_issuesevent(raw: dict) -> None:
    """Handle an IssuesEvent from GitHub."""
    return _handle_event(domain.GithubEventType.IssuesEvent, raw)


def handle_issuecommentevent(raw: dict) -> None:
    """Handle an IssueCommentEvent from GitHub."""
    return _handle_event(domain.GithubEventType.IssueCommentEvent, raw)


def _handle_event(event_type: domain.GithubEventType, raw: dict) -> None:
    issue_key: Optional[str] = None
    comment_id: Optional[str] = None

    gh_event = parse_github_event(event_type, raw)

    database.store_github_event(gh_event)

    if domain.is_gh_update_event(gh_event):
        issue_key = database.get_jira_issue_key(gh_event['issue']['id'])
        if domain.is_gh_comment_event(gh_event):
            comment_id = database.get_jira_comment_id(gh_event['comment']['id'])

    j_event = jira.propagate(translate_event(gh_event, issue_key, comment_id))

    if domain.is_creation_event(j_event):
        if domain.is_comment_event(j_event):
            database.store_comment_mapping(gh_event['comment']['id'],
                                           j_event['comment']['id'])
        else:
            database.store_issue_mapping(gh_event['issue']['id'],
                                         j_event['issue']['key'])
    return {}, HTTPStatus.OK, {}