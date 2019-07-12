

from datetime import datetime
from enum import Enum
from typing import Optional
from typing_extensions import TypedDict



class GithubEventType(Enum):
    IssuesEvent = 'IssuesEvent'
    IssueCommentEvent = 'IssueCommentEvent'


class GithubAction(Enum):
    opened = 'opened'
    edited = 'edited'
    deleted = 'deleted'
    transferred = 'transferred'
    pinned = 'pinned'
    unpinned = 'unpinned'
    closed = 'closed'
    reopened = 'reopened'
    assigned = 'assigned'
    unassigned = 'unassigned'
    labeled = 'labeled'
    unlabeled = 'unlabeled'
    locked = 'locked'
    unlocked = 'unlocked'
    milestoned = 'milestoned'
    demilestoned = 'demilestoned'
    created = 'created'


class GithubEventActionType(Enum):
    issue_opened = (GithubEventType.IssuesEvent, GithubAction.opened)
    issue_edited = (GithubEventType.IssuesEvent, GithubAction.edited)
    issue_deleted = (GithubEventType.IssuesEvent, GithubAction.deleted)
    issue_transferred = (GithubEventType.IssuesEvent, GithubAction.transferred)
    issue_pinned = (GithubEventType.IssuesEvent, GithubAction.pinned)
    issue_unpinned = (GithubEventType.IssuesEvent, GithubAction.unpinned)
    issue_closed = (GithubEventType.IssuesEvent, GithubAction.closed)
    issue_reopened = (GithubEventType.IssuesEvent, GithubAction.reopened)
    issue_assigned = (GithubEventType.IssuesEvent, GithubAction.assigned)
    issue_unassigned = (GithubEventType.IssuesEvent, GithubAction.unassigned)
    issue_labeled = (GithubEventType.IssuesEvent, GithubAction.labeled)
    issue_unlabeled = (GithubEventType.IssuesEvent, GithubAction.unlabeled)
    issue_locked = (GithubEventType.IssuesEvent, GithubAction.locked)
    issue_unlocked = (GithubEventType.IssuesEvent, GithubAction.unlocked)
    issue_milestoned = (GithubEventType.IssuesEvent, GithubAction.milestoned)
    issue_demilestoned = (GithubEventType.IssuesEvent, GithubAction.demilestoned)
    comment_created = (GithubEventType.IssueCommentEvent, GithubAction.created)
    comment_edited = (GithubEventType.IssueCommentEvent, GithubAction.edited)
    comment_deleted = (GithubEventType.IssueCommentEvent, GithubAction.deleted)


class GithubRepository:
    id: int
    name: str


class GithubUser(TypedDict):
    id: int
    login: str
    html_url: str


class GithubIssue(TypedDict):
    id: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime
    html_url: str
    user: GithubUser


class GithubComment(TypedDict):
    id: int
    body: str
    created_at: datetime
    updated_at: datetime
    html_url: str
    user: GithubUser


class GithubEvent(TypedDict):
    id: int
    event_type: GithubEventActionType
    repository: GithubRepository
    issue: GithubIssue
    comment: Optional[GithubComment]


class JiraEventType(Enum):
    issue_create = 'issue_create'
    issue_update = 'issue_update'
    issue_delete = 'issue_delete'
    issue_transition = 'issue_transition'
    comment_create = 'comment_create'
    comment_edit = 'comment_update'
    comment_delete = 'comment_delete'


class _Project(TypedDict):
    key: str


class _IssueType(TypedDict):
    name: str


class _JiraStatus(TypedDict):
    id: int


class JiraIssue(TypedDict):
    key: Optional[str]
    summary: str
    description: str
    issuetype: _IssueType
    project: _Project
    assignee: Optional[str]
    status: _JiraStatus


class JiraComment(TypedDict):
    id: str
    body: str


class JiraEvent(TypedDict):
    event_type: JiraEventType
    time: datetime
    issue: JiraIssue
    comment: Optional[JiraComment]


def is_comment_event(jira_event: JiraEvent) -> bool:
    return bool(jira_event['event_type'].value.startswith('comment_'))


def is_gh_comment_event(gh_event: GithubEvent) -> bool:
    return bool(gh_event['event_type'].name.startswith('comment_'))


def is_gh_update_event(gh_event: GithubEvent) -> bool:
    return bool(not gh_event['event_type'].name.endswith('_create'))


def is_creation_event(jira_event) -> bool:
    return bool(jira_event['event_type'].value.endswith('_create'))


def is_update_event(jira_event) -> bool:
    return bool(not jira_event['event_type'].value.endswith('_create'))