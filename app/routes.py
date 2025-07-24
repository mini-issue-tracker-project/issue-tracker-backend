from flask import Blueprint, jsonify, request
from .models import Issue
from . import db

main = Blueprint("main", __name__)

@main.route("/")
def hello():
    return "Hello from Issue Tracker backend!"

@main.route("/api/issues", methods=["GET"])
def get_issues():
    issues = Issue.query.all()
    return jsonify([{
        "id": issue.id,
        "title": issue.title,
        "description": issue.description,
        "status": issue.status
    } for issue in issues])

@main.route("/api/issues", methods=["POST"])
def create_issue():
    data = request.get_json()
    new_issue = Issue(
        title=data["title"],
        description=data["description"],
        status=data["status"]
    )
    db.session.add(new_issue)
    db.session.commit()
    return jsonify({
        "id": new_issue.id,
        "title": new_issue.title,
        "description": new_issue.description,
        "status": new_issue.status
    }), 201
