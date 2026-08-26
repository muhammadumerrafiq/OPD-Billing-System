import os
import sys
import sqlite3
import hashlib
import logging
from datetime import datetime

class DatabaseManager:
    _instance = None
    _db_path = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path=None):
        if not hasattr(self, 'initialized'):
            if db_path is None:
                # Default path in the project folder
                if getattr(sys, 'frozen', False):
                    db_dir = os.path.join(os.path.dirname(sys.executable), "data")
                    self.db_path = os.path.join(db_dir, "opd_billing.db")
                    if not os.path.exists(self.db_path):
                        # Copy from bundled resource
                        bundled_db = os.path.join(sys._MEIPASS, "data", "opd_billing.db")
                        if os.path.exists(bundled_db):
                            import shutil
                            os.makedirs(db_dir, exist_ok=True)
                            try:
                                shutil.copy(bundled_db, self.db_path)
                            except Exception as e:
                                print(f"Error copying database: {e}")
                else:
                    db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
                    self.db_path = os.path.join(db_dir, "opd_billing.db")
            else:
                self.db_path = db_path
            self.initialized = True
            self.init_db()

    def get_connection(self):
        """Returns a connection to the SQLite database with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        """Initializes the database schema if tables do not exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL, -- 'Admin' or 'Receptionist'
            full_name TEXT NOT NULL
        );
        """)

        # Patients table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE NOT NULL,
            patient_name TEXT NOT NULL,
            father_name TEXT,
            gender TEXT,
            age INTEGER,
            phone TEXT,
            cnic TEXT,
            address TEXT,
            registration_date TEXT NOT NULL
        );
        """)

        # Doctors table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_name TEXT NOT NULL,
            specialization TEXT,
            consultation_fee REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Inactive'))
        );
        """)

        # Procedures table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS procedures (
            procedure_id INTEGER PRIMARY KEY AUTOINCREMENT,
            procedure_name TEXT NOT NULL,
            category TEXT NOT NULL, -- 'Aesthetic', 'ENT', 'General', 'Dental', etc.
            procedure_fee REAL NOT NULL DEFAULT 0.0
        );
        """)

        # Lab Tests table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lab_tests (
            test_id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT NOT NULL,
            test_fee REAL NOT NULL DEFAULT 0.0
        );
        """)

        # Bills table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            patient_id TEXT NOT NULL,
            subtotal REAL NOT NULL DEFAULT 0.0,
            discount REAL NOT NULL DEFAULT 0.0,
            grand_total REAL NOT NULL DEFAULT 0.0,
            payment_method TEXT NOT NULL, -- 'Cash', 'Card', 'Easypaisa', 'JazzCash'
            created_date TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE RESTRICT
        );
        """)

        # Bill Items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL, -- 'Doctor Consultation', 'Procedure', 'Lab Test', 'Medicine', 'Hospital Charges'
            quantity INTEGER NOT NULL DEFAULT 1,
            price REAL NOT NULL DEFAULT 0.0,
            total REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY (bill_id) REFERENCES bills (bill_id) ON DELETE CASCADE
        );
        """)

        # Settings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """)

        conn.commit()

        # Seed initial data if tables are empty
        self._seed_data(conn)
        conn.close()

    def _seed_data(self, conn):
        cursor = conn.cursor()

        # Check if users are present
        cursor.execute("SELECT COUNT(*) FROM users;")
        if cursor.fetchone()[0] == 0:
            # Seed users
            # admin / admin123
            salt_admin = "bismel_salt_1234"
            hash_admin = hashlib.sha256(("admin123" + salt_admin).encode('utf-8')).hexdigest()
            cursor.execute("INSERT INTO users (username, password_hash, salt, role, full_name) VALUES (?, ?, ?, ?, ?);",
                           ("admin", hash_admin, salt_admin, "Admin", "System Admin"))

            # receptionist / recep123
            salt_recep = "bismel_salt_5678"
            hash_recep = hashlib.sha256(("recep123" + salt_recep).encode('utf-8')).hexdigest()
            cursor.execute("INSERT INTO users (username, password_hash, salt, role, full_name) VALUES (?, ?, ?, ?, ?);",
                           ("receptionist", hash_recep, salt_recep, "Receptionist", "Front Desk Receptionist"))

        # Seed settings
        cursor.execute("SELECT COUNT(*) FROM settings;")
        if cursor.fetchone()[0] == 0:
            default_settings = [
                ("hospital_name", "Bismel Medical Center"),
                ("hospital_address", "Sector G-11 Markaz, Islamabad, Pakistan"),
                ("hospital_phone", "+92-51-1234567"),
                ("hospital_email", "info@bismelmedical.com"),
                ("invoice_prefix", "INV"),
                ("invoice_footer", "Thank You For Visiting Bismel Medical Center"),
                ("theme", "Light")
            ]
            cursor.executemany("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?);", default_settings)

        # Seed doctors for demo purposes if empty
        cursor.execute("SELECT COUNT(*) FROM doctors;")
        if cursor.fetchone()[0] == 0:
            doctors = [
                ("Dr. Sarah Khan", "General Physician", 1500.0, "Active"),
                ("Dr. Ahmed Ali", "ENT Specialist", 2000.0, "Active"),
                ("Dr. Maria Zainab", "Aesthetician", 3000.0, "Active"),
                ("Dr. Usman Faisal", "Cardiologist", 2500.0, "Active")
            ]
            cursor.executemany("INSERT INTO doctors (doctor_name, specialization, consultation_fee, status) VALUES (?, ?, ?, ?);", doctors)

        # Seed procedures from official list
        cursor.execute("SELECT COUNT(*) FROM procedures;")
        proc_count = cursor.fetchone()[0]
        if proc_count == 0 or proc_count == 10:
            cursor.execute("DELETE FROM procedures;")
            procedures = [
                ("Hydra Facial (7 in 1)", "Aesthetic", 4000.0),
                ("Hydra Facial (12 in 1)", "Aesthetic", 6000.0),
                ("Carbon Peel Face", "Aesthetic", 4000.0),
                ("Face Laser", "Aesthetic", 4000.0),
                ("Arms Laser", "Aesthetic", 6000.0),
                ("Legs Laser", "Aesthetic", 7000.0),
                ("Full Body Laser", "Aesthetic", 18000.0),
                ("Hair PRP with (Serum)", "Aesthetic", 12000.0),
                ("Hair PRP with (Plasma)", "Aesthetic", 10000.0),
                ("Face PRP with (Serum)", "Aesthetic", 12000.0),
                ("Face PRP with (Plasma)", "Aesthetic", 10000.0),
                ("Microneedling", "Aesthetic", 6000.0),
                ("Mesotherapy", "Aesthetic", 6000.0),
                ("Tattoo Removal", "Aesthetic", 5000.0),
                ("Birth Mark Removal", "Aesthetic", 5000.0),
                ("Hair PRP with Mesotherapy", "Aesthetic", 15000.0),
                ("Face PRP with Mesotherapy", "Aesthetic", 15000.0),
                ("Slimming Drips", "Aesthetic", 12000.0),
                ("Hands Carbon Peel", "Aesthetic", 5000.0),
                ("Foot Carbon Peel", "Aesthetic", 5000.0),
                ("Carbon Peel Neck", "Aesthetic", 3000.0),
                ("Face + Neck Laser", "Aesthetic", 6000.0),
                ("Face + Neck Carbon Peel", "Aesthetic", 6000.0),
                ("LED Mask", "Aesthetic", 500.0),
                ("Blackheads & Whiteheads Removal", "Aesthetic", 1000.0),
                ("Whitening Drip", "Aesthetic", 12000.0)
            ]
            cursor.executemany("INSERT INTO procedures (procedure_name, category, procedure_fee) VALUES (?, ?, ?);", procedures)

        # Seed lab tests from Excel sheet or fall back to demo list
        cursor.execute("SELECT value FROM settings WHERE key = 'excel_tests_imported';")
        row = cursor.fetchone()
        if not row or row[0] != "true":
            # Clear previous tests
            cursor.execute("DELETE FROM lab_tests;")
            
            if getattr(sys, 'frozen', False):
                excel_path = os.path.join(sys._MEIPASS, "CDC Wah Pathology Rate List.xlsx")
            else:
                excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "CDC Wah Pathology Rate List.xlsx")
            imported_from_excel = False
            
            if os.path.exists(excel_path):
                try:
                    import pandas as pd
                    df = pd.read_excel(excel_path, skiprows=3, names=['S_No', 'Profile_Name', 'Final_Price'])
                    lab_tests = []
                    for _, r in df.iterrows():
                        name = str(r['Profile_Name']).strip()
                        price = float(r['Final_Price'])
                        lab_tests.append((name, price))
                    
                    if lab_tests:
                        cursor.executemany("INSERT INTO lab_tests (test_name, test_fee) VALUES (?, ?);", lab_tests)
                        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('excel_tests_imported', 'true');")
                        logging.info(f"Successfully imported {len(lab_tests)} lab tests from Excel.")
                        imported_from_excel = True
                except Exception as ex:
                    logging.error(f"Error reading or seeding from excel: {str(ex)}")
            
            if not imported_from_excel:
                # Fallback to old demo tests if excel file is missing or failed
                lab_tests = [
                    ("CBC (Complete Blood Count)", 800.0),
                    ("LFT (Liver Function Test)", 1800.0),
                    ("RFT (Renal Function Test)", 1500.0),
                    ("Blood Sugar (Fasting/Random)", 200.0),
                    ("Lipid Profile", 2200.0),
                    ("Thyroid Profile (T3, T4, TSH)", 2500.0),
                    ("HbA1c", 1200.0),
                    ("Urine Routine Examination", 400.0)
                ]
                cursor.executemany("INSERT INTO lab_tests (test_name, test_fee) VALUES (?, ?);", lab_tests)

        conn.commit()

    def backup_database(self, backup_filepath):
        """Creates a copy of the database to backup_filepath."""
        try:
            conn = self.get_connection()
            backup_conn = sqlite3.connect(backup_filepath)
            conn.backup(backup_conn)
            backup_conn.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Failed to backup database: {str(e)}")
            return False

    def restore_database(self, restore_filepath):
        """Restores the database from a backup copy."""
        try:
            restore_conn = sqlite3.connect(restore_filepath)
            conn = sqlite3.connect(self.db_path)
            restore_conn.backup(conn)
            conn.close()
            restore_conn.close()
            # Re-initialize to ensure everything is fine
            self.init_db()
            return True
        except Exception as e:
            logging.error(f"Failed to restore database: {str(e)}")
            return False
