from database.db_manager import DatabaseManager
from utils.logger import logger

class LabTest:
    @staticmethod
    def add_lab_test(name, fee):
        """Adds a laboratory test."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO lab_tests (test_name, test_fee)
                    VALUES (?, ?);
                """, (name, fee))
                conn.commit()
                logger.info(f"Added lab test: {name}")
                return True
        except Exception as e:
            logger.error(f"Failed to add lab test {name}: {str(e)}")
            return False

    @staticmethod
    def update_lab_test(test_id, name, fee):
        """Updates lab test details."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE lab_tests
                    SET test_name = ?, test_fee = ?
                    WHERE test_id = ?;
                """, (name, fee, test_id))
                conn.commit()
                logger.info(f"Updated lab test ID: {test_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to update lab test ID {test_id}: {str(e)}")
            return False

    @staticmethod
    def delete_lab_test(test_id):
        """Deletes a lab test."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM lab_tests WHERE test_id = ?;", (test_id,))
                conn.commit()
                logger.info(f"Deleted lab test ID: {test_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete lab test ID {test_id}: {str(e)}")
            return False

    @staticmethod
    def get_all_lab_tests():
        """Fetches all lab tests."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM lab_tests ORDER BY test_name ASC;")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching all lab tests: {str(e)}")
            return []

    @staticmethod
    def get_total_count():
        """Returns total lab test count."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM lab_tests;")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting lab test count: {str(e)}")
            return 0
