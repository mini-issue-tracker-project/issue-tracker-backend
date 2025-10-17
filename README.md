# Issue Tracker Backend

A Flask-based REST API backend for the Issue Tracker application. Provides endpoints for managing issues, comments, tags, users, and authentication.

---

## Tech Stack

- **Flask**: Web framework
- **PostgreSQL**: Database
- **SQLAlchemy**: ORM
- **Flask-JWT-Extended**: Authentication
- **Alembic**: Database migrations
- **Flask-CORS**: Cross-origin resource sharing

---

## Requirements

- Python 3.9 or higher
- PostgreSQL 15, 16, 17, or 18
- pip

---

## Complete Setup Guide

Follow these steps to set up the backend from scratch.

### Step 1: Install PostgreSQL

Download and install PostgreSQL for Windows:
- Visit: https://www.postgresql.org/download/windows/
- Download the installer for PostgreSQL 17 or 18
- Run the installer and remember your `postgres` user password
- Default port: `5432`

After installation, PostgreSQL should be running as a Windows service.

### Step 2: Create Database and User

Open PowerShell and run these commands:

```powershell
# Set your PostgreSQL path (adjust version: 17 or 18)
$psql = "C:\Program Files\PostgreSQL\17\bin\psql.exe"

# Create database user
& $psql -U postgres -c "CREATE USER issuetracker WITH PASSWORD 'issuetracker123';"

# Create database
& $psql -U postgres -c "CREATE DATABASE issuetracker OWNER issuetracker;"

# Grant privileges
& $psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE issuetracker TO issuetracker;"
```

**Note**: You'll be prompted for the `postgres` user password that you set during installation.

### Step 3: Clone and Setup Backend

```powershell
cd issue-tracker-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the `issue-tracker-backend` directory:

```env
DATABASE_URL=postgresql://issuetracker:issuetracker123@localhost:5432/issuetracker
JWT_SECRET_KEY=your-secret-key-change-in-production-abc123xyz
ALLOWED_ORIGINS=http://localhost:3000
```

**Important**: Change the `JWT_SECRET_KEY` to a secure random string in production.

### Step 5: Initialize Database Tables

Run the initialization script to create all tables:

```powershell
python scripts/init_db.py
```

You should see: `All tables created successfully!`

This creates the following tables:
- `users` - User accounts
- `issues` - Issue tickets
- `comments` - Comments on issues
- `statuses` - Issue status options
- `priorities` - Priority levels
- `tags` - Issue tags
- `issues_tags` - Many-to-many relationship between issues and tags

### Step 6: Mark Migrations as Complete

```powershell
flask db stamp head
```

This marks all migrations as applied without actually running them (since we already created tables).

### Step 7: Load Initial Data

Load essential data (statuses, priorities, tags, and sample users):

```powershell
$psql = "C:\Program Files\PostgreSQL\17\bin\psql.exe"  # adjust version
& $psql -U issuetracker -d issuetracker -f seed_initial_data.sql
```

Password: `issuetracker123`

This creates:
- **5 Statuses**: Open, In Progress, Resolved, Closed, Reopened
- **4 Priorities**: Low, Medium, High, Critical
- **10 Tags**: bug, feature, enhancement, documentation, ui, backend, frontend, security, performance, testing
- **2 Sample Users**:
  - Admin: `admin@example.com` / `admin123`
  - User: `user@example.com` / `user123`

### Step 8: (Optional) Load Demo Issues

To populate the database with realistic demo issues and comments:

```powershell
python scripts/populate_demo_data.py
```

This creates 8 realistic issues with various statuses, priorities, and comments - perfect for demonstrations.

### Step 9: Start the Backend Server

```powershell
python run.py
```

The backend will run on: **http://localhost:5000**

You should see output like:
```
DEBUG: DATABASE_URL = postgresql://issuetracker:issuetracker123@localhost:5432/issuetracker
 * Running on http://127.0.0.1:5000
```

### Step 10: Verify Setup

Test the backend:

```powershell
# Test health endpoint
Invoke-WebRequest http://localhost:5000/ping

# Or open in browser:
# http://localhost:5000/ping
```

---

## Project Structure

```
issue-tracker-backend/
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── config.py         # Configuration
│   ├── models.py         # Database models
│   └── routes.py         # API endpoints
├── migrations/           # Alembic migrations
├── scripts/              # Utility scripts
│   ├── init_db.py        # Initialize database tables
│   └── populate_demo_data.py  # Populate demo data
├── seed_initial_data.sql # Initial data (statuses, priorities, tags, users)
├── database_schema.dbml  # Database schema diagram
├── .env                  # Environment variables (create this)
├── requirements.txt      # Python dependencies
├── run.py               # Application entry point
└── README.md            # This file
```

---

## Database Schema

See `database_schema.dbml` for the complete database schema. You can visualize it at https://dbdiagram.io/d by copying the contents of that file.

**Main Tables:**
- `users` - User authentication and profiles
- `issues` - Issue tracking (linked to users, statuses, priorities)
- `comments` - Comments on issues
- `statuses` - Available status options
- `priorities` - Priority levels
- `tags` - Categorization tags
- `issues_tags` - Many-to-many relationship

---

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login and get JWT token
- `GET /api/me` - Get current user info (requires auth)

### Issues
- `GET /api/issues` - List all issues (with filtering)
- `POST /api/issues` - Create new issue (requires auth)
- `GET /api/issues/<id>` - Get issue details
- `PUT /api/issues/<id>` - Update issue (requires auth)
- `DELETE /api/issues/<id>` - Delete issue (requires auth)

### Comments
- `GET /api/issues/<id>/comments` - Get comments for an issue
- `POST /api/issues/<id>/comments` - Add comment (requires auth)
- `PUT /api/comments/<id>` - Update comment (requires auth)
- `DELETE /api/comments/<id>` - Delete comment (requires auth)

### Tags, Statuses, Priorities
- `GET /api/tags` - List all tags
- `GET /api/statuses` - List all statuses
- `GET /api/priorities` - List all priorities
- Admin endpoints for managing these (requires admin role)

### Users
- `GET /api/users` - List all users (requires auth)
- Admin endpoints for user management

---

## Useful Database Commands

View data in the database:

```powershell
$psql = "C:\Program Files\PostgreSQL\17\bin\psql.exe"

# Connect to database
& $psql -U issuetracker -d issuetracker

# Inside psql:
\dt                           # List all tables
\d users                      # Describe users table
SELECT * FROM users;          # View all users
SELECT * FROM issues;         # View all issues
SELECT * FROM statuses;       # View statuses
\q                            # Quit
```

View issues with joins:

```powershell
& $psql -U issuetracker -d issuetracker -c "SELECT i.id, i.title, s.name as status, p.name as priority, u.name as author FROM issues i JOIN statuses s ON i.status_id = s.id JOIN priorities p ON i.priority_id = p.id JOIN users u ON i.author_id = u.id ORDER BY i.created_at DESC;"
```

---

## Troubleshooting

### psql command not found
Use the full path to psql:
```powershell
$psql = "C:\Program Files\PostgreSQL\17\bin\psql.exe"  # adjust version
& $psql -U postgres
```

### Database connection error
1. Check PostgreSQL service is running:
   ```powershell
   Get-Service -Name postgresql*
   ```
2. Verify `.env` file exists and has correct DATABASE_URL
3. Check that port 5432 is correct (not 5433)

### Migration errors
If you get migration errors, the database tables are already created using `init_db.py`, so just run:
```powershell
flask db stamp head
```

### Starting fresh
To completely reset the database:
```powershell
$psql = "C:\Program Files\PostgreSQL\17\bin\psql.exe"
& $psql -U postgres -c "DROP DATABASE issuetracker;"
& $psql -U postgres -c "CREATE DATABASE issuetracker OWNER issuetracker;"
```
Then repeat from Step 5.

---

## Next Steps

After setting up the backend, set up the frontend:
1. Navigate to `issue-tracker-frontend`
2. Follow the instructions in its README.md
3. Access the full application at http://localhost:3000

---

## Default Login Credentials

After loading seed data, you can login with:

- **Admin Account**: 
  - Email: `admin@example.com`
  - Password: `admin123`

- **Regular User**: 
  - Email: `user@example.com`
  - Password: `user123`

**⚠️ Change these passwords in production!**
