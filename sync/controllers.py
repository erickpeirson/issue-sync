from typing import Optional
from pprint import pprint
from http import HTTPStatus

from flask import current_app
from werkzeug.exceptions import BadRequest, InternalServerError

from . import domain
from .parse import parse_github_event, ParseFailed
from .services import database, jira
from .process import translate


def handle_issuesevent(raw: Optional[dict]) -> None:
    """Handle an IssuesEvent from GitHub."""
    if raw is None:
        raise BadRequest('No request payload')
    return _handle_event(domain.GithubEventType.IssuesEvent, raw)


def handle_issuecommentevent(raw: dict) -> None:
    """Handle an IssueCommentEvent from GitHub."""
    current_app.logger.debug('Got IssueCommentEvent with action %s',
                             raw['action'])
    return _handle_event(domain.GithubEventType.IssueCommentEvent, raw)


def _handle_event(event_type: domain.GithubEventType, raw: dict) -> None:
    issue_key: Optional[str] = None
    comment_id: Optional[str] = None

    try:
        gh_event = parse_github_event(event_type, raw)
    except ValueError as e:
        current_app.logger.error('Bad payload: %s', e)
        raise BadRequest('Malformed payload') from e
    except ParseFailed as e:
        current_app.logger.error('Could not parse payload: %s', raw)
        return {'reason': 'could not parse payload'}, HTTPStatus.ACCEPTED, {}

    database.store_github_event(gh_event)

    # Load the Jira issue key/comment ID if this is related to an existing
    # resource.
    try:
        if 'id' in gh_event['issue']:
            issue_key = database.get_jira_issue_key(gh_event['issue']['id'])
            current_app.logger.debug('Loaded issue key %s', issue_key)
        if 'comment' in gh_event and 'id' in gh_event['comment']:
            comment_id = database.get_jira_comment_id(gh_event['comment']['id'])
            current_app.logger.debug('Loaded comment id %s', comment_id)
    except KeyError as e:
        raise BadRequest('Malformed request payload') from e

    # Action!
    try:
        j_event = jira.propagate(translate(gh_event, issue_key, comment_id))
    except jira.PropagationFailed as e:
        current_app.logger.error('Failed to propagate event: %s', e)
        raise InternalServerError('Failed to propagate event') from e

    # Store any new mappings.
    if domain.is_creation_event(j_event) \
            and domain.is_gh_creation_event(gh_event):
        if domain.is_comment_event(j_event) \
                and domain.is_gh_comment_event(gh_event):
            database.store_comment_mapping(gh_event['comment']['id'],
                                           j_event['comment']['id'])
        else:
            database.store_issue_mapping(gh_event['issue']['id'],
                                         j_event['issue']['key'])
    return {'result': j_event}, HTTPStatus.OK, {}