# Gamified Environment Learning for Students

A web-based gamified learning platform with 4 user roles: Students, Teachers, Parents, and Admin.

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Setup MySQL database:
```
mysql -u root -p < setup.sql
```

3. Update database credentials in app.py (user, password)

4. Run the application:
```
python app.py
```

5. Open browser: http://localhost:5000

## Demo Accounts
- Students: john, mary
- Teacher: mr_smith
- Parent: mrs_johnson
- Admin: admin

## Features
- 4 role-based dashboards
- Student: Complete lessons, earn points
- Teacher: View student progress
- Parent: Monitor student performance
- Admin: Manage all users and view statistics
