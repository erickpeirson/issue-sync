import json
from datetime import datetime
from pytz import UTC

from . import domain


class ParseFailed(Exception):
    """Could not parse an event."""


def _parse_time(value: str) -> datetime:
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC)


def parse_github_event(event_type: domain.GithubEventType,
                       event: dict) -> domain.GithubEvent:
    try:
        action = domain.GithubAction(event['action'])
        event['event_type'] = domain.GithubEventActionType((event_type, action))
        event['issue']['created_at'] = _parse_time(event['issue']['created_at'])
        event['issue']['updated_at'] = _parse_time(event['issue']['updated_at'])
        if 'comment' in event:
            event['comment']['created_at'] \
                = _parse_time(event['comment']['created_at'])
            event['comment']['updated_at'] \
                = _parse_time(event['comment']['updated_at'])
    except KeyError as e:
        raise ParseFailed('Could not parse event') from e
    return event


