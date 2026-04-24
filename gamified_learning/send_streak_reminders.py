import mysql.connector
from datetime import date, timedelta
from email_service import send_streak_reminder_email

# Connect to database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="gamified_learning"
)

cursor = db.cursor(dictionary=True)

# Find students who haven't logged in today but have an active streak
today = date.today()

cursor.execute("""
    SELECT id, username, email, current_streak 
    FROM users 
    WHERE role = 'student' 
    AND approved = TRUE 
    AND email IS NOT NULL
    AND current_streak > 0
    AND (last_activity_date < %s OR last_activity_date IS NULL)
""", (today,))

students = cursor.fetchall()

print(f"Found {len(students)} students to remind")

for student in students:
    print(f"Sending reminder to {student['username']} ({student['email']})")
    send_streak_reminder_email(student['email'], student['username'], student['current_streak'])

cursor.close()
db.close()

print("Streak reminders sent successfully!")
