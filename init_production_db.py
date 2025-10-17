"""
Initialize production database on Render
Run this once after deploying to create tables and load seed data
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from app import create_app, db
from app.models import Status, Priority, Tag, User

# Load environment
load_dotenv()

app = create_app()

def init_production_database():
    """Initialize database with tables and seed data"""
    with app.app_context():
        print("Creating all tables...")
        db.create_all()
        print("✓ Tables created")
        
        # Check if data already exists
        if Status.query.first():
            print("Database already initialized!")
            return
        
        print("\nLoading seed data...")
        
        # Create Statuses
        statuses = [
            Status(name='Open', display_order=1),
            Status(name='In Progress', display_order=2),
            Status(name='Resolved', display_order=3),
            Status(name='Closed', display_order=4),
            Status(name='Reopened', display_order=5)
        ]
        db.session.add_all(statuses)
        print("✓ Statuses created")
        
        # Create Priorities
        priorities = [
            Priority(name='Low', display_order=1),
            Priority(name='Medium', display_order=2),
            Priority(name='High', display_order=3),
            Priority(name='Critical', display_order=4)
        ]
        db.session.add_all(priorities)
        print("✓ Priorities created")
        
        # Create Tags
        tags = [
            Tag(name='bug', color='#ef4444', display_order=1),
            Tag(name='feature', color='#22c55e', display_order=2),
            Tag(name='enhancement', color='#3b82f6', display_order=3),
            Tag(name='documentation', color='#8b5cf6', display_order=4),
            Tag(name='ui', color='#06b6d4', display_order=5),
            Tag(name='backend', color='#f59e0b', display_order=6),
            Tag(name='frontend', color='#ec4899', display_order=7),
            Tag(name='security', color='#dc2626', display_order=8),
            Tag(name='performance', color='#10b981', display_order=9),
            Tag(name='testing', color='#6366f1', display_order=10)
        ]
        db.session.add_all(tags)
        print("✓ Tags created")
        
        # Create Admin User
        admin = User(name='Admin User', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        print("✓ Admin user created")
        
        # Create Test User
        user = User(name='Test User', email='user@example.com', role='user')
        user.set_password('user123')
        db.session.add(user)
        print("✓ Test user created")
        
        db.session.commit()
        print("\n✅ Database initialized successfully!")
        print("\nDefault credentials:")
        print("  Admin: admin@example.com / admin123")
        print("  User:  user@example.com / user123")

if __name__ == "__main__":
    init_production_database()

