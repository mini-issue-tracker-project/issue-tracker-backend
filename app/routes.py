from flask import Blueprint, jsonify, request
from .models import Issue, Tag, User
from . import db, bcrypt, jwt
from flask_jwt_extended import create_access_token

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
        "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in issue.tags]  # Include color
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
    # Handle tags
    tag_ids = data.get("tags", None)
    if tag_ids is not None:
        issue.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    db.session.commit()
    return jsonify({
        "id": issue.id,
        "title": issue.title,
        "description": issue.description,
        "status": issue.status,
        "priority": issue.priority,  # Include priority
        "author": issue.author,  # Include author
        "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in issue.tags]  # Include color
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
    # Handle tags
    tag_ids = data.get("tags", [])
    if tag_ids:
        new_issue.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    db.session.add(new_issue)
    db.session.commit()
    return jsonify({
        "id": new_issue.id,
        "title": new_issue.title,
        "description": new_issue.description,
        "status": new_issue.status,
        "priority": new_issue.priority,  # Include priority
        "author": new_issue.author,  # Include author
        "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in new_issue.tags]  # Include color
    }), 201

@main.route("/api/tags", methods=["GET"])
def get_tags():
    tags = Tag.query.all()
    return jsonify([{ "id": tag.id, "name": tag.name, "color": tag.color } for tag in tags])

@main.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    # Validate all fields are present and non-empty
    if not name or not email or not password:
        return jsonify({"error": "All fields (name, email, password) are required."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 400
    user = User(name=name, email=email, role='user')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    access_token = create_access_token(identity=user.id)
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 201

@main.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password."}), 401
    access_token = create_access_token(identity=user.id)
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    })
