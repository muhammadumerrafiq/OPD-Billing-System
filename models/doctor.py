from database.db_manager import DatabaseManager
from utils.logger import logger

class Doctor:
    @staticmethod
    def add_doctor(name, specialization, fee, status="Active"):
        """Adds a new doctor to the clinic database."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO doctors (doctor_name, specialization, consultation_fee, status)
                    VALUES (?, ?, ?, ?);
                """, (name, specialization, fee, status))
                conn.commit()
                logger.info(f"Added doctor: {name}")
                return True
        except Exception as e:
            logger.error(f"Failed to add doctor {name}: {str(e)}")
            return False

    @staticmethod
    def update_doctor(doctor_id, name, specialization, fee, status):
        """Updates doctor details."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE doctors
                    SET doctor_name = ?, specialization = ?, consultation_fee = ?, status = ?
                    WHERE doctor_id = ?;
                """, (name, specialization, fee, status, doctor_id))
                conn.commit()
                logger.info(f"Updated doctor ID: {doctor_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to update doctor ID {doctor_id}: {str(e)}")
            return False

    @staticmethod
    def delete_doctor(doctor_id):
        """Deletes a doctor. Safe since no hard reference checks are built in SQLite default tables
        but we should warn or handle error if referenced in invoices."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM doctors WHERE doctor_id = ?;", (doctor_id,))
                conn.commit()
                logger.info(f"Deleted doctor ID: {doctor_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete doctor ID {doctor_id}: {str(e)}")
            return False

    @staticmethod
    def get_all_doctors():
        """Fetches all doctors."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM doctors ORDER BY doctor_id DESC;")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching all doctors: {str(e)}")
            return []

    @staticmethod
    def get_active_doctors():
        """Fetches only active doctors."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM doctors WHERE status = 'Active' ORDER BY doctor_name ASC;")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching active doctors: {str(e)}")
            return []

    @staticmethod
    def get_total_count():
        """Returns total doctor count."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM doctors;")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting doctor count: {str(e)}")
            return 0
