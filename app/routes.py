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
        "tags": [{"id": tag.id, "name": tag.name} for tag in issue.tags]  # Include tags
    } for issue in issues])

@main.route("/api/issues/<int:id>", methods=["PUT"])
def update_issue(id):
    data = request.get_json()
    issue = Issue.query.get_or_404(id)
    issue.title = data.get("title", issue.title)
    issue.description = data.get("description", issue.description)
    issue.status = data.get("status", issue.status)
    db.session.commit()
    return jsonify({
        "id": issue.id,
        "title": issue.title,
        "description": issue.description,
        "status": issue.status
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
