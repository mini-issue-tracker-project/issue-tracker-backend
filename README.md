# Issue Tracker

A simple full-stack issue tracking application that allows users to create, view, update, and delete issues such as bug reports or feature requests. The project is split into two parts: a frontend built with Next.js and a backend powered by Flask.

---

## Requirements

- Node.js (v18 or higher)
- Python (v3.9 or higher)
- pip

---

## Installation & Running

### Backend (Flask)

   ```bash
    cd issue-tracker-backend        # Navigate to the backend directory
    python -m venv venv             # Create and activate a virtual environment
    source venv/bin/activate        # On Windows: venv\Scripts\activate
    pip install -r requirements.txt # Install the dependencies
    python run.py                   # Run the backend server
```
The backend will run on: http://localhost:5000

## Testing Connection
- Visit http://localhost:3000 to view the frontend.
- Visit http://localhost:5000/ping to check the backend status.
