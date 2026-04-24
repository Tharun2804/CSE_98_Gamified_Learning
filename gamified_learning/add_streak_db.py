import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="gamified_learning"
)

cursor = db.cursor()

# Add streak columns to users table
try:
    cursor.execute("ALTER TABLE users ADD COLUMN current_streak INT DEFAULT 0")
    print("Added current_streak column")
except:
    print("current_streak column already exists")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN longest_streak INT DEFAULT 0")
    print("Added longest_streak column")
except:
    print("longest_streak column already exists")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN last_activity_date DATE")
    print("Added last_activity_date column")
except:
    print("last_activity_date column already exists")

# Create daily_activity table
try:
    cursor.execute("""
        CREATE TABLE daily_activity (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            activity_date DATE NOT NULL,
            lessons_completed INT DEFAULT 0,
            quizzes_attempted INT DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES users(id),
            UNIQUE KEY unique_daily_activity (student_id, activity_date)
        )
    """)
    print("Created daily_activity table")
except:
    print("daily_activity table already exists")

db.commit()
cursor.close()
db.close()

print("\nStreak system added successfully!")
