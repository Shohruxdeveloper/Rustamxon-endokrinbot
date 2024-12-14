import sqlite3
from datetime import datetime
import sqlite3
from threading import local
from datetime import datetime

class User:
    def __init__(self, user_id, full_name, phone_number=None, user_name=None, ref_count=0, created_at=None):
        self.user_id = user_id  # Telegram user's message_id
        self.full_name = full_name
        self.user_name = user_name
        self.phone_number = phone_number
        self.ref_count = ref_count
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.user_id,
            "full_name": self.full_name,
            "user_name": self.user_name,
            "phone_number": self.phone_number,
            "ref_count": self.ref_count,
            "created_at": self.created_at,
        }

    @staticmethod
    def validate(data):
        if not data.get("full_name") or not data.get("phone_number"):
            raise ValueError("Full name and phone number are required.")



class ThreadSafeSQLiteConnection:
    def __init__(self, db_name="users.db"):
        self.local_storage = local()
        self.db_name = db_name

    def get_connection(self):
        if not hasattr(self.local_storage, "connection"):
            self.local_storage.connection = sqlite3.connect(
                self.db_name, check_same_thread=False
            )
            self.local_storage.connection.row_factory = sqlite3.Row
        return self.local_storage.connection

    def close_connection(self):
        if hasattr(self.local_storage, "connection"):
            self.local_storage.connection.close()
            del self.local_storage.connection


class UserORM:
    def __init__(self, db_name="users.db"):
        self.db_manager = ThreadSafeSQLiteConnection(db_name)
        self.create_table()

    def create_table(self):
        connection = self.db_manager.get_connection()
        cursor = connection.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            user_name TEXT,
            phone_number TEXT,
            created_at TEXT NOT NULL,
            ref_count INTEGER DEFAULT 0
        )
        """
        cursor.execute(query)
        connection.commit()

    def create_user(self, user: User):
        # User.validate(user.to_dict())
        connection = self.db_manager.get_connection()
        cursor = connection.cursor()
        query = """
        INSERT INTO users (id, full_name, user_name, phone_number, created_at, ref_count)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            user.user_id, user.full_name, user.user_name, user.phone_number, user.created_at, user.ref_count
        ))
        connection.commit()
        return user.user_id

    def update_user(self, user_id, **kwargs):
        connection = self.db_manager.get_connection()
        cursor = connection.cursor()
        updates = []
        values = []
        for key, value in kwargs.items():
            updates.append(f"{key} = ?")
            values.append(value)

        values.append(user_id)
        query = f"""
        UPDATE users SET {', '.join(updates)} WHERE id = ?
        """
        cursor.execute(query, values)
        connection.commit()

    def delete_user(self, user_id):
        connection = self.db_manager.get_connection()
        cursor = connection.cursor()
        query = "DELETE FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        connection.commit()

    def count_users(self):
        connection = self.db_manager.get_connection()
        cursor = connection.cursor()
        query = "SELECT COUNT(*) AS count FROM users"
        cursor.execute(query)
        return cursor.fetchone()["count"]

    def get_user(self, user_id):
        connection = self.db_manager.get_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_users(self):
        connection = self.db_manager.get_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM users"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def add_increment(self, user_id, increment_by=1):
        connection = self.db_manager.get_connection()
        cursor = connection.cursor()
        query = """
        UPDATE users SET ref_count = ref_count + ? WHERE id = ?
        """
        cursor.execute(query, (increment_by, user_id))
        connection.commit()

    def close(self):
        self.db_manager.close_connection()

    def __del__(self):
        self.close()


# # Example usage
# if __name__ == "__main__":
#     orm = TelegramORM()

#     # Create a new user
#     user = User(user_id=123456, full_name="John Doe", phone_number="1234567890", user_name="johndoe")
#     user_id = orm.create_user(user)
#     print(f"Created user with ID: {user_id}")

#     # Update user
#     orm.update_user(user_id, full_name="Johnathan Doe", ref_count=5)
#     print("User updated.")

#     # Increment ref_count
#     orm.add_increment(user_id, increment_by=2)
#     print("Incremented ref_count.")

#     # Get single user
#     user = orm.get_user(user_id)
#     print("Fetched user:", user)

#     # Count users
#     count = orm.count_users()
#     print(f"Total users: {count}")

#     # Get all users
#     users = orm.get_all_users()
#     print("All users:", users)

#     # Delete user
#     orm.delete_user(user_id)
#     print("User deleted.")

#     # Confirm deletion
#     count = orm.count_users()
#     print(f"Total users after deletion: {count}")
