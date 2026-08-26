import hashlib
from database.db_manager import DatabaseManager
from utils.logger import logger

class User:
    def __init__(self, user_id, username, role, full_name):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.full_name = full_name

    @staticmethod
    def authenticate(username, password):
        """Authenticates a user and returns a User object if successful, else None."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, username, password_hash, salt, role, full_name FROM users WHERE username = ?;", (username,))
                row = cursor.fetchone()
                if row:
                    user_id, uname, stored_hash, salt, role, full_name = row
                    # Verify hash
                    calc_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
                    if calc_hash == stored_hash:
                        logger.info(f"User '{username}' logged in successfully.")
                        return User(user_id, uname, role, full_name)
            logger.warning(f"Failed login attempt for user '{username}'.")
        except Exception as e:
            logger.error(f"Error during authentication for '{username}': {str(e)}")
        return None

    @staticmethod
    def change_password(username, old_password, new_password):
        """Changes the password for a user after verifying the old password."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?;", (username,))
                row = cursor.fetchone()
                if row:
                    stored_hash, salt = row
                    calc_hash = hashlib.sha256((old_password + salt).encode('utf-8')).hexdigest()
                    if calc_hash == stored_hash:
                        new_hash = hashlib.sha256((new_password + salt).encode('utf-8')).hexdigest()
                        cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?;", (new_hash, username))
                        conn.commit()
                        logger.info(f"Password changed for user '{username}'.")
                        return True
        except Exception as e:
            logger.error(f"Error changing password for user '{username}': {str(e)}")
        return False
