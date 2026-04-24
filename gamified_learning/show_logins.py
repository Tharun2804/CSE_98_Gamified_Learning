import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="gamified_learning"
)

cursor = db.cursor(dictionary=True)
cursor.execute("SELECT username, password, role, full_name, approved FROM users ORDER BY role, id")
users = cursor.fetchall()

print("\n" + "="*70)
print("ALL LOGIN CREDENTIALS")
print("="*70)

for user in users:
    status = "APPROVED" if user['approved'] else "PENDING"
    print(f"\nRole: {user['role'].upper()}")
    print(f"Username: {user['username']}")
    print(f"Password: {user['password']}")
    print(f"Full Name: {user['full_name']}")
    print(f"Status: {status}")
    print("-"*70)

cursor.close()
db.close()
