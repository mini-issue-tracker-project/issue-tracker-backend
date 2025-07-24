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
        "status": issue.status,
        "priority": issue.priority,  # Include priority
        "author": issue.author,  # Include author
        "tags": [{"id": tag.id, "name": tag.name} for tag in issue.tags]
    } for issue in issues])

@main.route("/api/issues/<int:id>", methods=["PUT"])
def update_issue(id):
    data = request.get_json()
    issue = Issue.query.get_or_404(id)
    issue.title = data.get("title", issue.title)
    issue.description = data.get("description", issue.description)
    issue.status = data.get("status", issue.status)
    issue.priority = data.get("priority", issue.priority)  # Update priority
    issue.author = data.get("author", issue.author)  # Update author
    db.session.commit()
    return jsonify({
        "id": issue.id,
        "title": issue.title,
        "description": issue.description,
        "status": issue.status,
        "priority": issue.priority,  # Include priority
        "author": issue.author  # Include author
    })

@main.route("/api/issues/<int:id>", methods=["DELETE"])
def delete_issue(id):
    issue = Issue.query.get_or_404(id)
    db.session.delete(issue)
    db.session.commit()
    return jsonify({"message": "Issue deleted successfully"}), 204

@main.route("/api/issues", methods=["POST"])
def create_issue():
    data = request.get_json()
    new_issue = Issue(
        title=data["title"],
        description=data["description"],
        status=data["status"],
        priority=data.get("priority"),  # Handle priority
        author=data.get("author")  # Handle author
    )
    db.session.add(new_issue)
    db.session.commit()
    return jsonify({
        "id": new_issue.id,
        "title": new_issue.title,
        "description": new_issue.description,
        "status": new_issue.status,
        "priority": new_issue.priority,  # Include priority
        "author": new_issue.author  # Include author
    }), 201
