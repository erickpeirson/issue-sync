from typing import Optional
from json import dumps, loads
import sqlalchemy.types as types
from sqlalchemy import Column, DateTime, Integer, String, Text, JSON

from flask import Flask
from flask_sqlalchemy import SQLAlchemy, Model

db: SQLAlchemy = SQLAlchemy()


class FriendlyJSONType(types.TypeDecorator):
    """A SQLite-friendly JSON data type."""

    impl = types.TEXT

    def process_bind_param(self, obj: Optional[dict], dialect: str) \
            -> Optional[str]:
        """Serialize a dict to JSON."""
        if obj is not None:
            value: str = dumps(obj)
            return value
        return obj

    def process_result_value(self, value: str, dialect: str) -> Optional[dict]:
        """Deserialize JSON content to a dict."""
        if value is not None:
            obj: dict = loads(value)
            return obj
        return None


FriendlyJSON = JSON().with_variant(FriendlyJSONType, 'sqlite')


class GithubEvent(db.Model):
    """Model for GitHub events."""

    __tablename__ = 'github_event'

    event_id = Column(Integer, primary_key=True)
    event_type = Column(String(50))
    event_action = Column(String(50))
    created = Column(DateTime)
    body = Column(FriendlyJSON)


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


def get_jira_issue_key(github_issue_key: str) -> str:
    jira_issue_key = db.session.query(IssueMap.jira_issue_key) \
        .filter(IssueMap.github_issue_key==github_issue_key) \
        .first()
    return jira_issue_key


def get_jira_comment_id(github_comment_id: str) -> str:
    jira_comment_id = db.session.query(CommentMap.jira_comment_id) \
        .filter(CommentMap.github_comment_id==github_comment_id) \
        .first()
    return jira_comment_id