import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="gamified_learning"
)

cursor = db.cursor()

# Create certificates table
try:
    cursor.execute("""
        CREATE TABLE certificates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            certificate_path VARCHAR(255) NOT NULL,
            certificate_id VARCHAR(100) UNIQUE NOT NULL,
            issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id)
        )
    """)
    print("Created certificates table")
except:
    print("certificates table already exists")

db.commit()
cursor.close()
db.close()

print("\nCertificate system database setup complete!")
