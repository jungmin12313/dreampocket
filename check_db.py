from database import db

def main():
    print("Database check:")
    scholarships = db.get_all_scholarships()
    print(f"Total scholarships in database: {len(scholarships)}")
    if scholarships:
        print("Sample scholarships:")
        for s in scholarships[:5]:
            print(f"- {s['category']} | {s['title']} | {s['period']} | {s['status']}")
    
    # Check users
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"Total users in database: {user_count}")
    if user_count > 0:
        cursor.execute("SELECT * FROM users LIMIT 5")
        print("Sample users:")
        for row in cursor.fetchall():
            print(f"- User ID: {row[0]} | GPA: {row[1]} | Income: {row[2]} | Location: {row[3]} | Major: {row[4]}")

if __name__ == "__main__":
    main()
