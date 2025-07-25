from datetime import datetime, timezone

from . import db
from flask_bcrypt import Bcrypt

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False, server_default='')
    role = db.Column(db.String(20), nullable=False, default='user')
    issues = db.relationship('Issue', back_populates='assignee')
    comments = db.relationship('Comment', back_populates='author')

    def set_password(self, raw_password):
        bcrypt = Bcrypt()
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode('utf-8')

    def check_password(self, raw_password):
        bcrypt = Bcrypt()
        return bcrypt.check_password_hash(self.password_hash, raw_password)

class Issue(db.Model):
    __tablename__ = 'issues'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(50))
    author = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assignee = db.relationship('User', back_populates='issues')
    comments = db.relationship('Comment', back_populates='issue')
    tags = db.relationship('Tag', secondary='issues_tags', back_populates='issues')

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20))
    issues = db.relationship('Issue', secondary='issues_tags', back_populates='tags')

class IssueTag(db.Model):
    __tablename__ = 'issues_tags'
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', back_populates='comments')
    issue = db.relationship('Issue', back_populates='comments')