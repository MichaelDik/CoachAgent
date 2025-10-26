# ...existing code...
import os
import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASS", ""),
    "database": os.environ.get("DB_NAME", "testdb"),
}

def main():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS people (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                age INT
            )
        """)
        conn.commit()

        # parameterized insert (prevents SQL injection)
        cursor.execute("INSERT INTO people (name, age) VALUES (%s, %s)", ("Alice", 30))
        conn.commit()

        # select
        cursor.execute("SELECT id, name, age FROM people")
        for row in cursor.fetchall():
            print(row)

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied: check DB_USER/DB_PASS")
        else:
            print("DB error:", err)
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
# ...existing code...