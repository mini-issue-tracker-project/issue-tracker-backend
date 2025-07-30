from flask import Blueprint, jsonify, request
from .models import Issue, Tag, User, Comment
from . import db, bcrypt, jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

main = Blueprint("main", __name__)

@main.route("/")
def hello():
    return "Hello from Issue Tracker backend!"

@main.route("/api/issues", methods=["GET"])
def get_issues():
    # Parse query params
    try:
        skip = int(request.args.get("skip", 0))
    except (TypeError, ValueError):
        skip = 0
    try:
        limit = int(request.args.get("limit", 5))
    except (TypeError, ValueError):
        limit = 5
    status = request.args.get("status")
    priority = request.args.get("priority")
    author_id = request.args.get("author_id")
    tags = request.args.get("tags")
    tags_list = None
    if tags:
        try:
            tags_list = [int(t) for t in tags.split(",") if t.strip()]
        except Exception:
            tags_list = None

    # Build query
    q = Issue.query
    if status:
        q = q.filter(Issue.status == status)
    if priority:
        q = q.filter(Issue.priority == priority)
    if author_id:
        try:
            q = q.filter(Issue.author_id == int(author_id))
        except Exception:
            pass
    if tags_list:
        q = q.filter(Issue.tags.any(Tag.id.in_(tags_list)))
    total = q.count()
    items = q.offset(skip).limit(limit).all()

    def serialize_issue(issue):
        from .models import Comment
        comment_count = Comment.query.filter_by(issue_id=issue.id).count()
        return {
            "id": issue.id,
            "title": issue.title,
            "description": issue.description,
            "status": issue.status,
            "priority": issue.priority,
            "author": {"id": issue.author.id, "name": issue.author.name} if issue.author else None,
            "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in issue.tags],
            "comment_count": comment_count
        }

    return jsonify({
        "total_count": total,
        "skip": skip,
        "limit": limit,
        "data": [serialize_issue(issue) for issue in items]
    })

@main.route("/api/issues/<int:id>", methods=["PUT"])
@jwt_required()
def update_issue(id):
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    issue = Issue.query.get_or_404(id)
    if user.role != 'admin' and issue.author_id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    issue.title = data.get("title", issue.title)
    issue.description = data.get("description", issue.description)
    issue.status = data.get("status", issue.status)
    issue.priority = data.get("priority", issue.priority)  # Update priority
    # Do NOT update issue.author_id here!
    # Handle tags
    tag_ids = data.get("tags", None)
    if tag_ids is not None:
        issue.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    db.session.commit()
    author_obj = User.query.get(issue.author_id)
    return jsonify({
        "id": issue.id,
        "title": issue.title,
        "description": issue.description,
        "status": issue.status,
        "priority": issue.priority,  # Include priority
        "author": {"id": author_obj.id, "name": author_obj.name} if author_obj else None,
        "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in issue.tags]  # Include color
    })

@main.route("/api/issues/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_issue(id):
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    issue = Issue.query.get_or_404(id)
    if user.role != 'admin' and issue.author_id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    db.session.delete(issue)
    db.session.commit()
    return jsonify({"message": "Issue deleted successfully"}), 204

@main.route("/api/issues/<int:id>", methods=["GET"])
def get_issue(id):
    issue = Issue.query.get_or_404(id)
    return jsonify({
        "id": issue.id,
        "title": issue.title,
        "description": issue.description,
        "status": issue.status,
        "priority": issue.priority,
        "author": {"id": issue.author.id, "name": issue.author.name} if issue.author else None,
        "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in issue.tags]
    })

@main.route("/api/issues", methods=["POST"])
@jwt_required()
def create_issue():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    new_issue = Issue(
        title=data["title"],
        description=data["description"],
        status=data["status"],
        priority=data.get("priority"),  # Handle priority
        author_id=get_jwt_identity()
    )
    # Handle tags
    tag_ids = data.get("tags", [])
    if tag_ids:
        new_issue.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    db.session.add(new_issue)
    db.session.commit()
    author_obj = User.query.get(new_issue.author_id)
    return jsonify({
        "id": new_issue.id,
        "title": new_issue.title,
        "description": new_issue.description,
        "status": new_issue.status,
        "priority": new_issue.priority,  # Include priority
        "author": {"id": author_obj.id, "name": author_obj.name} if author_obj else None,
        "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in new_issue.tags]  # Include color
    }), 201

@main.route("/api/tags", methods=["GET"])
def get_tags():
    tags = Tag.query.all()
    return jsonify([{ "id": tag.id, "name": tag.name, "color": tag.color } for tag in tags])

@main.route("/api/tags", methods=["POST"])
@jwt_required()
def create_tag():
    user = User.query.get_or_404(int(get_jwt_identity()))
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json()
    name = data.get('name', '').strip()
    color = data.get('color', '').strip()
    if not name or not color:
        return jsonify({'error': 'Name and color are required.'}), 400
    tag = Tag(name=name, color=color)
    db.session.add(tag)
    db.session.commit()
    return jsonify({'id': tag.id, 'name': tag.name, 'color': tag.color}), 201

@main.route("/api/tags/<int:id>", methods=["PUT"])
@jwt_required()
def update_tag(id):
    user = User.query.get_or_404(int(get_jwt_identity()))
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    tag = Tag.query.get_or_404(id)
    data = request.get_json()
    name = data.get('name')
    color = data.get('color')
    if name is not None:
        tag.name = name.strip()
    if color is not None:
        tag.color = color.strip()
    db.session.commit()
    return jsonify({'id': tag.id, 'name': tag.name, 'color': tag.color})

@main.route("/api/tags/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_tag(id):
    user = User.query.get_or_404(int(get_jwt_identity()))
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    return jsonify({'message': 'Tag deleted successfully'}), 204

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
    access_token = create_access_token(identity=str(user.id))
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
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    })

@main.route("/api/issues/<int:issue_id>/comments", methods=["GET"])
def get_comments(issue_id):
    # Parse query params
    try:
        skip = int(request.args.get("skip", 0))
    except (TypeError, ValueError):
        skip = 0
    try:
        limit = int(request.args.get("limit", 10))
    except (TypeError, ValueError):
        limit = 10
    
    author_name = request.args.get("author_name")
    start_date = request.args.get("start")
    end_date = request.args.get("end")

    # Build query
    q = Comment.query.filter(Comment.issue_id == issue_id)
    
    if author_name:
        # Join with User table to filter by name
        q = q.join(User, Comment.author_id == User.id).filter(User.name.ilike(f"%{author_name}%"))
    
    if start_date:
        try:
            from datetime import datetime
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            q = q.filter(Comment.created_at >= start_dt)
        except Exception:
            pass
    
    if end_date:
        try:
            from datetime import datetime
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            q = q.filter(Comment.created_at <= end_dt)
        except Exception:
            pass
    
    total = q.count()
    comments = q.offset(skip).limit(limit).all()

    def serialize_comment(comment):
        return {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at.isoformat(),
            "author": {"id": comment.author.id, "name": comment.author.name} if comment.author else None
        }

    return jsonify({
        "total_count": total,
        "skip": skip,
        "limit": limit,
        "data": [serialize_comment(comment) for comment in comments]
    })

@main.route("/api/issues/<int:issue_id>/comments", methods=["POST"])
@jwt_required()
def create_comment(issue_id):
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data or not data.get("content"):
        return jsonify({"error": "Content is required"}), 400
    
    new_comment = Comment(
        issue_id=issue_id,
        author_id=user_id,
        content=data["content"]
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({
        "id": new_comment.id,
        "content": new_comment.content,
        "created_at": new_comment.created_at.isoformat(),
        "author": {"id": user.id, "name": user.name}
    }), 201

@main.route("/api/comments/<int:comment_id>", methods=["PUT"])
@jwt_required()
def update_comment(comment_id):
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    comment = Comment.query.get_or_404(comment_id)
    
    if user.role != 'admin' and comment.author_id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    
    data = request.get_json()
    if not data or not data.get("content"):
        return jsonify({"error": "Content is required"}), 400
    
    comment.content = data["content"]
    db.session.commit()
    
    return jsonify({
        "id": comment.id,
        "content": comment.content,
        "created_at": comment.created_at.isoformat(),
        "author": {"id": comment.author.id, "name": comment.author.name} if comment.author else None
    })

@main.route("/api/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    comment = Comment.query.get_or_404(comment_id)
    
    if user.role != 'admin' and comment.author_id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({"message": "Comment deleted successfully"}), 204

@main.route("/api/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{ "id": user.id, "name": user.name, "email": user.email } for user in users])
