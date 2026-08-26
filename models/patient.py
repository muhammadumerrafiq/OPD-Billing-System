from datetime import datetime
from database.db_manager import DatabaseManager
from utils.logger import logger

class Patient:
    @staticmethod
    def generate_next_patient_id():
        """Generates the next unique patient ID (e.g., BMC-000001)."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(id) FROM patients;")
                row = cursor.fetchone()
                max_id = row[0] if row and row[0] is not None else 0
                next_id = max_id + 1
                return f"BMC-{next_id:06d}"
        except Exception as e:
            logger.error(f"Error generating patient ID: {str(e)}")
            return "BMC-000001" # Safe fallback

    @staticmethod
    def add_patient(name, father_name, gender, age, phone, cnic, address):
        """Registers a new patient and returns the auto-generated patient_id if successful, else None."""
        db = DatabaseManager()
        patient_id = Patient.generate_next_patient_id()
        reg_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO patients (patient_id, patient_name, father_name, gender, age, phone, cnic, address, registration_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (patient_id, name, father_name, gender, age, phone, cnic, address, reg_date))
                conn.commit()
                logger.info(f"Registered new patient {patient_id}: {name}")
                return patient_id
        except Exception as e:
            logger.error(f"Failed to register patient: {str(e)}")
            return None

    @staticmethod
    def update_patient(patient_id, name, father_name, gender, age, phone, cnic, address):
        """Updates patient records."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE patients
                    SET patient_name = ?, father_name = ?, gender = ?, age = ?, phone = ?, cnic = ?, address = ?
                    WHERE patient_id = ?;
                """, (name, father_name, gender, age, phone, cnic, address, patient_id))
                conn.commit()
                logger.info(f"Updated patient details for {patient_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to update patient {patient_id}: {str(e)}")
            return False

    @staticmethod
    def delete_patient(patient_id):
        """Deletes a patient record. Note: This will fail if patient has bills (PRAGMA foreign_keys = ON)."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM patients WHERE patient_id = ?;", (patient_id,))
                conn.commit()
                logger.info(f"Deleted patient {patient_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete patient {patient_id}: {str(e)}")
            return False

    @staticmethod
    def get_patient(patient_id):
        """Fetches a single patient record as a dictionary."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients WHERE patient_id = ?;", (patient_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
        except Exception as e:
            logger.error(f"Failed to fetch patient {patient_id}: {str(e)}")
        return None

    @staticmethod
    def search_patients(search_query):
        """Searches patients by ID, name, or phone."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                # Wildcard search
                term = f"%{search_query}%"
                cursor.execute("""
                    SELECT * FROM patients
                    WHERE patient_id LIKE ? OR patient_name LIKE ? OR phone LIKE ? OR cnic LIKE ?
                    ORDER BY id DESC;
                """, (term, term, term, term))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error searching patients: {str(e)}")
            return []

    @staticmethod
    def get_all_patients(limit=1000):
        """Returns all registered patients."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients ORDER BY id DESC LIMIT ?;", (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching all patients: {str(e)}")
            return []

    @staticmethod
    def get_total_count():
        """Returns total patient count."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM patients;")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting patient count: {str(e)}")
            return 0
