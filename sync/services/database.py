from typing import Optional
from json import dumps, loads
from datetime import datetime

from pytz import UTC
from flask import Flask
import sqlalchemy.types as types
from sqlalchemy import Column, DateTime, Integer, String, Text, JSON
from flask_sqlalchemy import SQLAlchemy, Model
from sqlalchemy.orm.exc import NoResultFound

from arxiv.util.serialize import ISO8601JSONDecoder
from ..serialize import EnumJSONEncoder
from ..domain import GithubEvent, JiraEvent

db: SQLAlchemy = SQLAlchemy()


class Nada(Exception):
    """Zilch."""


class FriendlyJSONType(types.TypeDecorator):
    """A SQLite-friendly JSON data type."""

    impl = types.TEXT

    def process_bind_param(self, obj: Optional[dict], dialect: str) \
            -> Optional[str]:
        """Serialize a dict to JSON."""
        if obj is not None:
            value: str = dumps(obj, cls=EnumJSONEncoder)
            return value
        return obj

    def process_result_value(self, value: str, dialect: str) -> Optional[dict]:
        """Deserialize JSON content to a dict."""
        if value is not None:
            obj: dict = loads(value, cls=ISO8601JSONDecoder)
            return obj
        return None


# FriendlyJSON = JSON().with_variant(FriendlyJSONType, 'sqlite') \
#     .with_variant(FriendlyJSONType, 'mysql')


class DBGithubEvent(db.Model):
    """Model for GitHub events."""

    __tablename__ = 'github_event'

    event_id = Column(Integer, primary_key=True)
    event_type = Column(String(50))
    event_action = Column(String(50))
    created = Column(DateTime)
    body = Column(FriendlyJSONType)


class IssueMap(db.Model):

    __tablename__ = 'issue_map'

    github_issue_id = Column(Integer, primary_key=True)
    jira_issue_key = Column(String(50), primary_key=True)


class CommentMap(db.Model):

    __tablename__ = 'comment_map'

    github_comment_id = Column(Integer, primary_key=True)
    jira_comment_id = Column(String(50), primary_key=True)



def init_app(app: Flask) -> None:
    db.init_app(app)


def create_all() -> None:
    db.create_all()


def get_jira_issue_key(github_issue_id: str) -> Optional[str]:
    result = db.session.query(IssueMap.jira_issue_key) \
        .filter(IssueMap.github_issue_id==github_issue_id) \
        .first()
    if isinstance(result, tuple):
        return result[0]
    return None


def get_jira_comment_id(github_comment_id: str) -> Optional[str]:
    result = db.session.query(CommentMap.jira_comment_id) \
        .filter(CommentMap.github_comment_id==github_comment_id) \
        .first()
    if isinstance(result, tuple):
        return result[0]
    return None


def store_github_event(gh_event: GithubEvent) -> GithubEvent:
    db.session.add(DBGithubEvent(
        event_type=gh_event['event_type'].value[0].value,
        event_action=gh_event['action'],
        created=datetime.now(UTC),
        body=gh_event
    ))
    db.session.commit()
    return gh_event


def store_comment_mapping(gh_comment_id: str, jira_comment_id: str) -> None:
    db.session.add(CommentMap(github_comment_id=gh_comment_id,
                              jira_comment_id=jira_comment_id))
    db.session.commit()


def store_issue_mapping(gh_issue_id: int, jira_issue_key: str) -> None:
    db.session.add(IssueMap(github_issue_id=gh_issue_id,
                            jira_issue_key=jira_issue_key))
    db.session.commit()
