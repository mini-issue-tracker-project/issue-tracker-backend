# Issue Tracker Backend

Flask REST API backend for the Issue Tracker application.

🌐 **Live Demo:** https://issue-tracker-frontend-phi.vercel.app

---

## Tech Stack

- Flask + PostgreSQL
- SQLAlchemy ORM
- JWT Authentication
- Flask-CORS

---

## Local Setup

### 1. Install PostgreSQL

Download from: https://www.postgresql.org/download/

### 2. Create Database

```powershell
$psql = "C:\Program Files\PostgreSQL\17\bin\psql.exe"  # adjust version

& $psql -U postgres -c "CREATE USER issuetracker WITH PASSWORD 'issuetracker123';"
& $psql -U postgres -c "CREATE DATABASE issuetracker OWNER issuetracker;"
```

### 3. Install Dependencies

```powershell
cd issue-tracker-backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Configure Environment

Create `.env` file:

```env
DATABASE_URL=postgresql://issuetracker:issuetracker123@localhost:5432/issuetracker
JWT_SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000
```

### 5. Initialize Database

```powershell
# Create tables
python scripts/init_db.py

# Mark migrations as complete
flask db stamp head

# Load initial data (statuses, priorities, tags, users)
& $psql -U issuetracker -d issuetracker -f scripts/seed_initial_data.sql
```

Password: `issuetracker123`

### 6. (Optional) Add Demo Data

```powershell
python scripts/populate_demo_data.py
```

### 7. Start Server

```powershell
python run.py
```

Backend runs on: **http://localhost:5000**

---

## Default Credentials

After loading seed data:

- **Admin**: `admin@example.com` / `admin123`
- **User**: `user@example.com` / `user123`

---

## Project Structure

```
issue-tracker-backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   └── routes.py
├── scripts/
│   ├── init_db.py              # Create tables
│   ├── populate_demo_data.py   # Add demo issues
│   └── seed_initial_data.sql   # Initial data (local only)
├── migrations/                  # Alembic (keep folder)
├── database_schema.dbml         # DB diagram for dbdiagram.io
├── .env                         # Environment variables (create this)
└── run.py                       # Entry point
```

---

## API Endpoints

- `POST /api/register` - Register user
- `POST /api/login` - Login
- `GET /api/issues` - List issues
- `POST /api/issues` - Create issue (auth required)
- `GET /api/issues/:id/comments` - Get comments
- `POST /api/issues/:id/comments` - Add comment (auth required)
- `GET /api/tags` - List tags
- `GET /api/statuses` - List statuses
- `GET /api/priorities` - List priorities

---

## Deployment (Render)

The app is deployed using HTTP endpoints (no shell needed):

1. Create PostgreSQL database on Render
2. Deploy backend service
3. Set environment variables in Render
4. Call `POST https://your-backend.onrender.com/initialize-db` to setup
5. Call `POST https://your-backend.onrender.com/add-demo-issues` for demo data

---

## Database Schema

View the schema: Copy `database_schema.dbml` content to https://dbdiagram.io/d

---

## Troubleshooting

**Database connection fails:**
- Check PostgreSQL is running
- Verify DATABASE_URL in `.env` file
- Ensure port is 5432

**Import errors:**
- Activate virtual environment: `.\venv\Scripts\Activate.ps1`
- Reinstall dependencies: `pip install -r requirements.txt`
