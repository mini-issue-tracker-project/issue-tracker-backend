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

### 5. Start Server

```powershell
python run.py
```

Backend runs on: **http://localhost:5000**

### 6. Initialize Database

**Check backend is running:**
```
GET http://localhost:5000/ping
```

**Create tables and load initial data:**
```
POST http://localhost:5000/initialize-db
```

Response includes default user credentials:
```json
{
  "status": "success",
  "credentials": {
    "admin": {"email": "admin@example.com", "password": "admin123"},
    "user": {"email": "user@example.com", "password": "user123"}
  }
}
```

This endpoint:
- Creates all database tables (users, issues, comments, tags, etc.)
- Loads statuses, priorities, and tags
- Creates admin and test users with properly hashed passwords

**Add demo issues (optional):**
```
POST http://localhost:5000/add-demo-issues
```

Creates 3 sample issues with comments for demonstration.

---

## How to Call Endpoints

Use any HTTP client:
- **Browser:** Postman, Insomnia, or REST Client extensions
- **Command line:** `curl -X POST http://localhost:5000/initialize-db`
- **PowerShell:** `Invoke-WebRequest -Uri http://localhost:5000/initialize-db -Method POST`
- **Python:** `requests.post('http://localhost:5000/initialize-db')`

---

## Default Credentials

- **Admin**: `admin@example.com` / `admin123`
- **User**: `user@example.com` / `user123`

---

## API Endpoints

### Setup Endpoints (Call Once)
- `GET /ping` - Health check
- `POST /initialize-db` - Create tables and load initial data
- `POST /add-demo-issues` - Add 3 demo issues with comments

### Main Endpoints
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

## Why the `scripts/init_db.py` file?

**Optional convenience script** that pre-creates empty tables before starting the server.

- **Without it:** Just start the server and call `/initialize-db` - it will create tables AND load data
- **With it:** Pre-create empty tables, then start server, then call `/initialize-db` to load data

**You don't need to use it** - `/initialize-db` endpoint does everything. It's just there if you want to separate table creation from data loading.

To use it:
```powershell
python scripts/init_db.py  # Creates empty tables
flask db stamp head        # Marks migrations as done
```

---

## Project Structure

```
issue-tracker-backend/
├── app/
│   ├── routes.py        # Includes /initialize-db and /add-demo-issues
│   ├── models.py        # Database models
│   └── config.py
├── scripts/
│   └── init_db.py       # Optional: pre-create tables
├── .env                 # Create this
└── run.py
```

---

## Troubleshooting

**Database connection fails:**
- Check PostgreSQL is running
- Verify DATABASE_URL in `.env` file

**Import errors:**
- Activate virtual environment: `.\venv\Scripts\Activate.ps1`
- Run: `pip install -r requirements.txt`
