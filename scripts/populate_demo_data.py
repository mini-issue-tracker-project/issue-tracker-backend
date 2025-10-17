"""
Populate demo data for issue tracker - realistic issues and comments
Uses existing users from the database
"""
from pathlib import Path
from dotenv import load_dotenv
import os
import sys
from datetime import datetime, timezone, timedelta
import random

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Load .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from app import create_app, db
from app.models import User, Issue, Tag, Comment, Status, Priority

app = create_app()

def populate_demo_issues():
    with app.app_context():
        # Get existing users
        users = User.query.all()
        if len(users) < 2:
            print("❌ Error: Need at least 2 users in the database.")
            print("\nPlease either:")
            print("1. Sign up users through the web interface at http://localhost:3000")
            print("2. Use the default users from seed_initial_data.sql")
            return
        
        print(f"✓ Found {len(users)} users:")
        for user in users:
            print(f"  - {user.name} ({user.email})")
        
        # Get statuses and priorities
        status_open = Status.query.filter_by(name='Open').first()
        status_in_progress = Status.query.filter_by(name='In Progress').first()
        status_resolved = Status.query.filter_by(name='Resolved').first()
        status_closed = Status.query.filter_by(name='Closed').first()
        
        priority_low = Priority.query.filter_by(name='Low').first()
        priority_medium = Priority.query.filter_by(name='Medium').first()
        priority_high = Priority.query.filter_by(name='High').first()
        priority_critical = Priority.query.filter_by(name='Critical').first()
        
        # Get tags
        tag_bug = Tag.query.filter_by(name='bug').first()
        tag_feature = Tag.query.filter_by(name='feature').first()
        tag_enhancement = Tag.query.filter_by(name='enhancement').first()
        tag_ui = Tag.query.filter_by(name='ui').first()
        tag_backend = Tag.query.filter_by(name='backend').first()
        tag_frontend = Tag.query.filter_by(name='frontend').first()
        tag_security = Tag.query.filter_by(name='security').first()
        tag_performance = Tag.query.filter_by(name='performance').first()
        
        # Create realistic issues
        issues_data = [
            {
                'title': 'User authentication fails on mobile devices',
                'description': 'Users report that login functionality does not work properly on mobile browsers. The issue appears to be related to session handling.',
                'status': status_open,
                'priority': priority_critical,
                'author': users[0],
                'tags': [tag_bug, tag_security, tag_frontend],
                'comments': [
                    {'author': users[1], 'content': 'I can reproduce this on iOS Safari. JWT token seems to expire immediately.'},
                    {'author': users[0], 'content': 'Investigating the token storage mechanism. Might be related to localStorage limitations.'}
                ]
            },
            {
                'title': 'Add dark mode support to the application',
                'description': 'Implement a dark mode theme for better user experience during night time usage. Should include a toggle in the settings.',
                'status': status_in_progress,
                'priority': priority_medium,
                'author': users[1] if len(users) > 1 else users[0],
                'tags': [tag_feature, tag_ui, tag_enhancement],
                'comments': [
                    {'author': users[0], 'content': 'Started working on the CSS variables for theming.'},
                    {'author': users[1] if len(users) > 1 else users[0], 'content': 'Should we persist the user preference in the database?'}
                ]
            },
            {
                'title': 'Implement pagination for issues list',
                'description': 'Current issues list loads all records at once, causing performance issues with large datasets. Need to implement server-side pagination.',
                'status': status_open,
                'priority': priority_high,
                'author': users[0],
                'tags': [tag_enhancement, tag_performance, tag_backend],
                'comments': [
                    {'author': users[0], 'content': 'Planning to implement cursor-based pagination for better performance.'}
                ]
            },
            {
                'title': 'Fix typo in dashboard header',
                'description': 'The word "Issue" is misspelled as "Isseu" in the main dashboard header.',
                'status': status_closed,
                'priority': priority_low,
                'author': users[1] if len(users) > 1 else users[0],
                'tags': [tag_bug, tag_frontend],
                'comments': []
            },
            {
                'title': 'Add email notifications for issue updates',
                'description': 'Users should receive email notifications when they are mentioned in comments or when issues assigned to them are updated.',
                'status': status_open,
                'priority': priority_medium,
                'author': users[0],
                'tags': [tag_feature, tag_backend],
                'comments': [
                    {'author': users[1] if len(users) > 1 else users[0], 'content': 'We should use a queue system like Celery for sending emails asynchronously.'},
                    {'author': users[0], 'content': 'Good idea. Will also need to add email preferences to user settings.'}
                ]
            },
            {
                'title': 'Optimize database queries for issue filtering',
                'description': 'The filtering mechanism is causing slow response times. Need to add proper indexes and optimize the queries.',
                'status': status_resolved,
                'priority': priority_high,
                'author': users[1] if len(users) > 1 else users[0],
                'tags': [tag_performance, tag_backend],
                'comments': [
                    {'author': users[0], 'content': 'Added indexes on status_id, priority_id, and author_id columns.'},
                    {'author': users[1] if len(users) > 1 else users[0], 'content': 'Performance improved by 70%. Closing this issue.'}
                ]
            },
            {
                'title': 'Issue creation form validation improvements',
                'description': 'Enhance client-side validation for the issue creation form. Add clear error messages and field highlighting.',
                'status': status_in_progress,
                'priority': priority_medium,
                'author': users[0],
                'tags': [tag_enhancement, tag_frontend, tag_ui],
                'comments': []
            },
            {
                'title': 'API rate limiting implementation',
                'description': 'Implement rate limiting on API endpoints to prevent abuse and ensure fair usage. Consider using Redis for distributed rate limiting.',
                'status': status_open,
                'priority': priority_high,
                'author': users[1] if len(users) > 1 else users[0],
                'tags': [tag_security, tag_backend],
                'comments': [
                    {'author': users[0], 'content': 'Flask-Limiter looks like a good option for this.'}
                ]
            }
        ]
        
        # Create issues with staggered creation times (more realistic)
        base_time = datetime.now(timezone.utc) - timedelta(days=7)
        
        print("\n🔨 Creating demo issues...")
        
        for idx, issue_data in enumerate(issues_data):
            # Create issue with realistic timestamp
            issue = Issue(
                title=issue_data['title'],
                description=issue_data['description'],
                status_id=issue_data['status'].id,
                priority_id=issue_data['priority'].id,
                author_id=issue_data['author'].id,
                created_at=base_time + timedelta(days=idx, hours=random.randint(0, 23)),
                updated_at=base_time + timedelta(days=idx, hours=random.randint(0, 23))
            )
            
            # Add tags
            issue.tags = issue_data['tags']
            
            db.session.add(issue)
            db.session.flush()  # Get the issue ID
            
            # Add comments with realistic timestamps
            for comment_idx, comment_data in enumerate(issue_data['comments']):
                comment = Comment(
                    issue_id=issue.id,
                    author_id=comment_data['author'].id,
                    content=comment_data['content'],
                    created_at=issue.created_at + timedelta(hours=random.randint(1, 24), minutes=random.randint(0, 59)),
                    updated_at=issue.created_at + timedelta(hours=random.randint(1, 24), minutes=random.randint(0, 59))
                )
                db.session.add(comment)
            
            print(f"  ✓ {issue.title}")
        
        db.session.commit()
        
        print(f"\n✅ Successfully created {len(issues_data)} issues with comments!")
        print(f"\n📊 Issues by status:")
        for status in [status_open, status_in_progress, status_resolved, status_closed]:
            count = Issue.query.filter_by(status_id=status.id).count()
            if count > 0:
                print(f"   {status.name}: {count}")
        
        print("\n🎉 Demo data population complete!")
        print("\nYou can now:")
        print("   - View issues at http://localhost:3000")
        print("   - Login with admin@example.com / admin123")

if __name__ == "__main__":
    populate_demo_issues()

