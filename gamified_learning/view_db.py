import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="gamified_learning"
)

cursor = db.cursor(dictionary=True)

print("\n=== USERS ===")
cursor.execute("SELECT * FROM users")
for row in cursor.fetchall():
    print(row)

print("\n=== LESSONS ===")
cursor.execute("SELECT * FROM lessons")
for row in cursor.fetchall():
    print(row)

print("\n=== QUIZZES ===")
cursor.execute("SELECT * FROM quizzes")
for row in cursor.fetchall():
    print(row)

cursor.close()
db.close()
