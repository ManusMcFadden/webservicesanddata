import sqlite3

def migrate_user_table():
    conn = sqlite3.connect("tennis.db")
    cursor = conn.cursor()
    
    try:
        print("Adding 'is_admin' column to 'users' table...")
        # 1. Add the column with a default value of 0 (False)
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        conn.commit()
        print("✅ Column added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️ Column already exists, skipping...")
        else:
            print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_user_table()