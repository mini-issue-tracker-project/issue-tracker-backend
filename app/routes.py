from flask import Blueprint, jsonify, request
from .models import Issue, Tag, User, Comment, Status, Priority
from . import db, bcrypt, jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

main = Blueprint("main", __name__)

def serialize_issue(issue):
    comment_count = Comment.query.filter_by(issue_id=issue.id).count()
    return {
        "id": issue.id,
        "title": issue.title,
        "description": issue.description,
        "status": {"id": issue.status.id, "name": issue.status.name} if issue.status else None,
        "priority": {"id": issue.priority.id, "name": issue.priority.name} if issue.priority else None,
        "author": {"id": issue.author.id, "name": issue.author.name} if issue.author else None,
        "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in issue.tags],
        "created_at": issue.created_at.isoformat() if issue.created_at else None,
        "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
        "comment_count": comment_count
    }

def serialize_comment(comment):
    return {
        "id": comment.id,
        "content": comment.content,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
        "updated_at": comment.updated_at.isoformat() if comment.updated_at else None,
        "author": {"id": comment.author.id, "name": comment.author.name} if comment.author else None,
        "issue": {"id": comment.issue.id, "title": comment.issue.title} if comment.issue else None
    }

@main.route("/")
def hello():
    return "Hello from Issue Tracker backend!"

@main.route("/api/issues", methods=["GET"])
def get_issues():
    try:
        # Parse query params
        try:
            skip = int(request.args.get("skip", 0))
        except (TypeError, ValueError):
            skip = 0
        try:
            limit = int(request.args.get("limit", 5))
        except (TypeError, ValueError):
            limit = 5
        status_id = request.args.get("status_id")
        priority_id = request.args.get("priority_id")
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
        if status_id:
            try:
                q = q.filter(Issue.status_id == int(status_id))
            except Exception:
                pass
        if priority_id:
            try:
                q = q.filter(Issue.priority_id == int(priority_id))
            except Exception:
                pass
        if author_id:
            try:
                q = q.filter(Issue.author_id == int(author_id))
            except Exception:
                pass
        if tags_list:
            q = q.filter(Issue.tags.any(Tag.id.in_(tags_list)))
        total = q.count()
        items = q.order_by(Issue.updated_at.desc()).offset(skip).limit(limit).all()

        return jsonify({
            "total_count": total,
            "skip": skip,
            "limit": limit,
            "data": [serialize_issue(issue) for issue in items]
        })
    except Exception as e:
        print(f"Error in get_issues: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

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
    if "status_id" in data:
        issue.status_id = data["status_id"]
    if "priority_id" in data:
        issue.priority_id = data["priority_id"]
    # Do NOT update issue.author_id here!
    # Handle tags
    tag_ids = data.get("tags", None)
    if tag_ids is not None:
        issue.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    db.session.commit()
    return jsonify(serialize_issue(issue))

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
    return jsonify(serialize_issue(issue))

@main.route("/api/issues", methods=["POST"])
@jwt_required()
def create_issue():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    title = data.get("title")
    description = data.get("description", "")
    status_id = data.get("status_id")
    priority_id = data.get("priority_id")

    if not title:
        return jsonify({"error": "Title is required."}), 400

    if status_id is None:
        return jsonify({"error": "status_id cannot be null."}), 400
    if priority_id is None:
        return jsonify({"error": "priority_id cannot be null."}), 400

    try:
        status_id = int(status_id)
        priority_id = int(priority_id)
    except (ValueError, TypeError):
        return jsonify({"error": "status_id and priority_id must be integers."}), 400

    status = Status.query.get(status_id)
    if not status:
        return jsonify({"error": "Invalid status_id."}), 400
    priority = Priority.query.get(priority_id)
    if not priority:
        return jsonify({"error": "Invalid priority_id."}), 400

    new_issue = Issue(
        title=title,
        description=description,
        status_id=status_id,
        priority_id=priority_id,
        author_id=user_id
    )
    tag_ids = data.get("tags", [])
    if tag_ids:
        new_issue.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    db.session.add(new_issue)
    db.session.commit()
    return jsonify(serialize_issue(new_issue)), 201


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
    comments = q.order_by(Comment.updated_at.desc()).offset(skip).limit(limit).all()

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
        "updated_at": new_comment.updated_at.isoformat(),
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
        "updated_at": comment.updated_at.isoformat(),
        "author": {"id": comment.author.id, "name": comment.author.name} if comment.author else None
    })

@main.route("/api/comments", methods=["GET"])
@jwt_required()
def get_all_comments():
    try:
        # Parse query params
        try:
            skip = int(request.args.get("skip", 0))
        except (TypeError, ValueError):
            skip = 0
        try:
            limit = int(request.args.get("limit", 10))
        except (TypeError, ValueError):
            limit = 10
        
        author_id = request.args.get("author_id")
        issue_id = request.args.get("issue_id")
        start_date = request.args.get("start")
        end_date = request.args.get("end")

        # Build query
        q = Comment.query
        
        if author_id:
            try:
                q = q.filter(Comment.author_id == int(author_id))
            except (ValueError, TypeError):
                pass
        
        if issue_id:
            try:
                q = q.filter(Comment.issue_id == int(issue_id))
            except (ValueError, TypeError):
                pass
        
        if start_date:
            try:
                from datetime import datetime
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                q = q.filter(Comment.updated_at >= start_dt)
            except Exception:
                pass
        
        if end_date:
            try:
                from datetime import datetime
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                q = q.filter(Comment.updated_at <= end_dt)
            except Exception:
                pass
        
        total = q.count()
        comments = q.order_by(Comment.updated_at.desc()).offset(skip).limit(limit).all()

        return jsonify({
            "total_count": total,
            "skip": skip,
            "limit": limit,
            "data": [serialize_comment(comment) for comment in comments]
        })
    except Exception as e:
        print(f"Error in get_all_comments: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

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

# --- Statuses CRUD ---
@main.route('/api/statuses', methods=['GET'])
def get_statuses():
    statuses = Status.query.all()
    return jsonify([{ 'id': s.id, 'name': s.name } for s in statuses])

@main.route('/api/statuses', methods=['POST'])
@jwt_required()
def create_status():
    user = User.query.get_or_404(int(get_jwt_identity()))
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name is required.'}), 400
    if Status.query.filter_by(name=name).first():
        return jsonify({'error': 'Status already exists.'}), 400
    status = Status(name=name)
    db.session.add(status)
    db.session.commit()
    return jsonify({'id': status.id, 'name': status.name}), 201

@main.route('/api/statuses/<int:id>', methods=['PUT'])
@jwt_required()
def update_status(id):
    user = User.query.get_or_404(int(get_jwt_identity()))
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    status = Status.query.get_or_404(id)
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name is required.'}), 400
    if Status.query.filter(Status.name == name, Status.id != id).first():
        return jsonify({'error': 'Status already exists.'}), 400
    status.name = name
    db.session.commit()
    return jsonify({'id': status.id, 'name': status.name})

@main.route('/api/statuses/<int:id>/usage', methods=['GET'])
@jwt_required()
def get_status_usage(id):
    user = User.query.get_or_404(int(get_jwt_identity()))
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    status = Status.query.get_or_404(id)
    
    affected_issues = Issue.query.filter_by(status_id=id).all()
    return jsonify({
        "status": {"id": status.id, "name": status.name},
        "affected_issues": [{"id": issue.id, "title": issue.title} for issue in affected_issues],
        "count": len(affected_issues)
    })

@main.route('/api/statuses/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_status(id):
    user = User.query.get_or_404(int(get_jwt_identity()))
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    status = Status.query.get_or_404(id)
    
    # Check if status is in use by any issues
    affected_issues = Issue.query.filter_by(status_id=id).all()
    if affected_issues:
        return jsonify({
            "error": "Cannot delete, in use",
            "message": "Please change the statuses of these issues since they have the status that you want to delete.",
            "affected_issues": [{"id": issue.id, "title": issue.title} for issue in affected_issues]
        }), 409
    
    db.session.delete(status)
    db.session.commit()
    return jsonify({'message': 'Status deleted successfully'}), 204

# --- Priorities CRUD ---
@main.route('/api/priorities', methods=['GET'])
def get_priorities():
    priorities = Priority.query.all()
    return jsonify([{ 'id': p.id, 'name': p.name } for p in priorities])

@main.route('/api/priorities', methods=['POST'])
@jwt_required()
def create_priority():
    user = User.query.get_or_404(int(get_jwt_identity()))
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name is required.'}), 400
    if Priority.query.filter_by(name=name).first():
        return jsonify({'error': 'Priority already exists.'}), 400
    priority = Priority(name=name)
    db.session.add(priority)
    db.session.commit()
    return jsonify({'id': priority.id, 'name': priority.name}), 201

@main.route('/api/priorities/<int:id>', methods=['PUT'])
@jwt_required()
def update_priority(id):
    user = User.query.get_or_404(int(get_jwt_identity()))
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    priority = Priority.query.get_or_404(id)
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name is required.'}), 400
    if Priority.query.filter(Priority.name == name, Priority.id != id).first():
        return jsonify({'error': 'Priority already exists.'}), 400
    priority.name = name
    db.session.commit()
    return jsonify({'id': priority.id, 'name': priority.name})

@main.route('/api/priorities/<int:id>/usage', methods=['GET'])
@jwt_required()
def get_priority_usage(id):
    user = User.query.get_or_404(int(get_jwt_identity()))
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    priority = Priority.query.get_or_404(id)
    
    affected_issues = Issue.query.filter_by(priority_id=id).all()
    return jsonify({
        "priority": {"id": priority.id, "name": priority.name},
        "affected_issues": [{"id": issue.id, "title": issue.title} for issue in affected_issues],
        "count": len(affected_issues)
    })

@main.route('/api/priorities/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_priority(id):
    user = User.query.get_or_404(int(get_jwt_identity()))
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    priority = Priority.query.get_or_404(id)
    
    # Check if priority is in use by any issues
    affected_issues = Issue.query.filter_by(priority_id=id).all()
    if affected_issues:
        return jsonify({
            "error": "Cannot delete, in use",
            "message": "Please change the priorities of these issues since they have the priority that you want to delete.",
            "affected_issues": [{"id": issue.id, "title": issue.title} for issue in affected_issues]
        }), 409
    
    db.session.delete(priority)
    db.session.commit()
    return jsonify({'message': 'Priority deleted successfully'}), 204

# --- User Profile Endpoints ---
@main.route('/api/users/<int:id>', methods=['GET'])
@jwt_required()
def get_user_profile(id):
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get_or_404(current_user_id)
        target_user = User.query.get_or_404(id)
        
        # Authorization: only the user themselves or an admin can view the profile
        if current_user.role != 'admin' and current_user.id != target_user.id:
            return jsonify({'error': 'Forbidden'}), 403
        
        # Get status_id from query params for dynamic filtering
        status_id = request.args.get("status_id")
        
        # Calculate stats
        total_issues = Issue.query.filter_by(author_id=target_user.id).count()
        total_comments = Comment.query.filter_by(author_id=target_user.id).count()
        
        # Calculate filtered issues count based on status_id
        filtered_issues_count = 0
        if status_id:
            try:
                filtered_issues_count = Issue.query.filter_by(
                    author_id=target_user.id, 
                    status_id=int(status_id)
                ).count()
            except (ValueError, TypeError):
                # If status_id is invalid, default to 0
                filtered_issues_count = 0
        else:
            # Default to "open" status if no status_id provided
            open_status = Status.query.filter_by(name='open').first()
            if open_status:
                filtered_issues_count = Issue.query.filter_by(
                    author_id=target_user.id, 
                    status_id=open_status.id
                ).count()
        
        # Get user's issues (compact form)
        user_issues = Issue.query.filter_by(author_id=target_user.id).order_by(Issue.updated_at.desc()).limit(10).all()
        my_issues = []
        for issue in user_issues:
            try:
                my_issues.append({
                    "id": issue.id,
                    "title": issue.title,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "status": {"id": issue.status.id, "name": issue.status.name} if issue.status else None,
                    "priority": {"id": issue.priority.id, "name": issue.priority.name} if issue.priority else None
                })
            except Exception as e:
                print(f"Error processing issue {issue.id}: {e}")
                # Skip this issue if there's an error
                continue
        
        # Get user's comments (compact form)
        user_comments = Comment.query.filter_by(author_id=target_user.id).order_by(Comment.updated_at.desc()).limit(10).all()
        my_comments = []
        for comment in user_comments:
            try:
                my_comments.append({
                    "id": comment.id,
                    "content": comment.content,
                    "updated_at": comment.updated_at.isoformat(),
                    "issue": {"id": comment.issue.id, "title": comment.issue.title} if comment.issue else None
                })
            except Exception as e:
                print(f"Error processing comment {comment.id}: {e}")
                # Skip this comment if there's an error
                continue
        
        return jsonify({
            "id": target_user.id,
            "name": target_user.name,
            "email": target_user.email,
            "role": target_user.role,
            "stats": {
                "total_issues": total_issues,
                "filtered_issues_count": filtered_issues_count,
                "total_comments": total_comments
            },
            "my_issues": my_issues,
            "my_comments": my_comments
        })
    except Exception as e:
        print(f"Error in get_user_profile for user {id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@main.route('/api/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user_profile(id):
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get_or_404(current_user_id)
    target_user = User.query.get_or_404(id)
    
    # Authorization: only the user themselves or an admin can update the profile
    if current_user.role != 'admin' and current_user.id != target_user.id:
        return jsonify({'error': 'Forbidden'}), 403
    
    data = request.get_json() or {}
    
    # Update name if provided
    if 'name' in data:
        new_name = data['name'].strip()
        if not new_name:
            return jsonify({'error': 'Name cannot be empty'}), 400
        target_user.name = new_name
    
    # Update password if provided
    if 'password' in data:
        new_password = data['password']
        if not new_password:
            return jsonify({'error': 'Password cannot be empty'}), 400
        target_user.set_password(new_password)
    
    db.session.commit()
    
    # Return updated user info (excluding password hash)
    return jsonify({
        "id": target_user.id,
        "name": target_user.name,
        "email": target_user.email,
        "role": target_user.role
    })

@main.route("/api/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{ "id": user.id, "name": user.name, "email": user.email } for user in users])
