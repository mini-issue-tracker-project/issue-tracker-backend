from app import db, create_app
from app.models import User, Issue, Tag, Comment

def populate_database():
    # Create users
    user1 = User(name="Kemal", email="kemal@example.com")
    user2 = User(name="John Doe", email="john@example.com")
    user3 = User(name="Jane Smith", email="jane@example.com")

    # Create tags
    tag_ui = Tag(name="ui", color="blue")
    tag_bug = Tag(name="bug", color="red")
    tag_feature = Tag(name="feature", color="green")
    tag_enhancement = Tag(name="enhancement", color="yellow")
    tag_documentation = Tag(name="documentation", color="purple")

    # Add users and tags to the session
    db.session.add_all([user1, user2, user3, tag_ui, tag_bug, tag_feature, tag_enhancement, tag_documentation])
    db.session.commit()

    # Create issues
    issue1 = Issue(
        title="Fix login bug",
        description="There is a login bug we need to fix.",
        status="open",
        priority="high",
        author=user1,
        tags=[tag_bug],
        comments=[
            Comment(author=user2, content="I noticed this happens only on mobile."),
            Comment(author=user3, content="Working on this right now.")
        ]
    )

    issue2 = Issue(
        title="Login page not responsive",
        description="The login page is not responsive on mobile devices.",
        status="open",
        priority="high",
        author=user2,
        tags=[tag_bug, tag_enhancement],
        comments=[]
    )

    issue3 = Issue(
        title="Add dark mode support",
        description="Add dark mode support to the application.",
        status="in_progress",
        priority="medium",
        author=user3,
        tags=[tag_feature, tag_ui],
        comments=[]
    )

    issue4 = Issue(
        title="Fix typo in About page",
        description="Fix the typo in the About page.",
        status="closed",
        priority="low",
        author=user2,
        tags=[tag_bug, tag_enhancement],
        comments=[]
    )

    # Add issues to the session
    db.session.add_all([issue1, issue2, issue3, issue4])
    db.session.commit()

if __name__ == "__main__":
    app = create_app()  # Ensure you have a create_app function in your app module
    with app.app_context():
        populate_database()
        print("Database populated with dummy data.")
