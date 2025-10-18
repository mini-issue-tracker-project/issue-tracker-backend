"""
Initialize database tables from SQLAlchemy models.
This script creates all tables defined in app/models.py
"""
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Load .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Verify environment variables loaded
database_url = os.getenv('DATABASE_URL')
if not database_url or 'default_user' in database_url:
    print("❌ Error: DATABASE_URL not properly set in .env file")
    print(f"Current value: {database_url}")
    print("\nPlease create a .env file with:")
    print("DATABASE_URL=postgresql://issuetracker:issuetracker123@localhost:5432/issuetracker")
    sys.exit(1)

print(f"✓ DATABASE_URL loaded: {database_url}")

from app import create_app, db

app = create_app()

def init_database():
    """Create all database tables"""
    with app.app_context():
        print("\n🔨 Creating database tables...")
        db.create_all()
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"\n✅ Successfully created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   - {table}")
        
        print("\n📝 Next steps:")
        print("   1. Run: flask db stamp head")
        print("   2. Start server: python run.py")
        print("   3. Initialize data: POST http://localhost:5000/initialize-db")
        print("   4. (Optional) Add demo issues: POST http://localhost:5000/add-demo-issues")

if __name__ == "__main__":
    init_database()

