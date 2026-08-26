from database.db_manager import DatabaseManager
from utils.logger import logger

class Procedure:
    @staticmethod
    def add_procedure(name, category, fee):
        """Adds a medical procedure."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO procedures (procedure_name, category, procedure_fee)
                    VALUES (?, ?, ?);
                """, (name, category, fee))
                conn.commit()
                logger.info(f"Added procedure: {name} under category: {category}")
                return True
        except Exception as e:
            logger.error(f"Failed to add procedure {name}: {str(e)}")
            return False

    @staticmethod
    def update_procedure(procedure_id, name, category, fee):
        """Updates procedure details."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE procedures
                    SET procedure_name = ?, category = ?, procedure_fee = ?
                    WHERE procedure_id = ?;
                """, (name, category, fee, procedure_id))
                conn.commit()
                logger.info(f"Updated procedure ID: {procedure_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to update procedure ID {procedure_id}: {str(e)}")
            return False

    @staticmethod
    def delete_procedure(procedure_id):
        """Deletes a procedure."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM procedures WHERE procedure_id = ?;", (procedure_id,))
                conn.commit()
                logger.info(f"Deleted procedure ID: {procedure_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete procedure ID {procedure_id}: {str(e)}")
            return False

    @staticmethod
    def get_all_procedures():
        """Fetches all procedures."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM procedures ORDER BY category ASC, procedure_name ASC;")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching all procedures: {str(e)}")
            return []

    @staticmethod
    def get_procedures_by_category(category):
        """Fetches procedures of a specific category."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM procedures WHERE category = ? ORDER BY procedure_name ASC;", (category,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching procedures by category {category}: {str(e)}")
            return []

    @staticmethod
    def get_categories():
        """Returns unique category list."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT category FROM procedures ORDER BY category ASC;")
                rows = cursor.fetchall()
                return [row[0] for row in rows if row[0]]
        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            return ["General", "Aesthetic", "ENT", "Dental", "Orthopedic"]

    @staticmethod
    def get_total_count():
        """Returns total procedures count."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM procedures;")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting procedure count: {str(e)}")
            return 0
