import os
from datetime import datetime
from models.user import User
from models.patient import Patient
from models.doctor import Doctor
from models.procedure import Procedure
from models.lab_test import LabTest
from models.bill import Bill
from database.db_manager import DatabaseManager
from utils.logger import logger
from utils.printer import PrinterManager
from views.widgets.toast import ToastNotification
from controllers.billing_controller import BillingController
from controllers.reports_controller import ReportsController

class MainController:
    def __init__(self, main_window, is_dark_mode=False):
        self.main_window = main_window
        self.is_dark = is_dark_mode
        self.db = DatabaseManager()
        
        # Instantiate views and register them to stack
        self.init_sub_controllers()
        self.bind_signals()
        
        # Initial data loading
        self.load_global_settings()
        self.refresh_dashboard()

    def init_sub_controllers(self):
        # We hook sub controllers to views registered on MainWindow
        self.billing_ctrl = BillingController(self.main_window.views["billing"], self.main_window)
        self.reports_ctrl = ReportsController(self.main_window.views["reports"], self.main_window)

    def bind_signals(self):
        # Window navigation
        self.main_window.page_changed.connect(self.on_page_changed)
        self.main_window.theme_toggled.connect(self.on_theme_toggled)

        # CRUD: Patients View Signals
        self.main_window.views["patient_reg"].register_requested.connect(self.add_patient)
        self.main_window.views["patient_reg"].update_requested.connect(self.update_patient)
        self.main_window.views["patient_reg"].delete_requested.connect(self.delete_patient)
        self.main_window.views["patient_reg"].print_slip_requested.connect(self.print_patient_slip)
        
        # Patient Records Search (linking both register and record grids to same data loading)
        self.main_window.views["patient_reg"].search_input.textChanged.connect(self.search_patients)
        self.main_window.views["patient_rec"].search_input.textChanged.connect(self.search_patients_rec)
        self.main_window.views["patient_rec"].update_requested.connect(self.update_patient_rec)
        self.main_window.views["patient_rec"].delete_requested.connect(self.delete_patient_rec)

        # CRUD: Doctors View Signals
        self.main_window.views["doctors"].add_requested.connect(self.add_doctor)
        self.main_window.views["doctors"].update_requested.connect(self.update_doctor)
        self.main_window.views["doctors"].delete_requested.connect(self.delete_doctor)

        # CRUD: Procedures View Signals
        self.main_window.views["procedures"].add_requested.connect(self.add_procedure)
        self.main_window.views["procedures"].update_requested.connect(self.update_procedure)
        self.main_window.views["procedures"].delete_requested.connect(self.delete_procedure)

        # CRUD: Lab Tests View Signals
        self.main_window.views["lab_tests"].add_requested.connect(self.add_lab_test)
        self.main_window.views["lab_tests"].update_requested.connect(self.update_lab_test)
        self.main_window.views["lab_tests"].delete_requested.connect(self.delete_lab_test)

        # Invoice History View Signals
        self.main_window.views["history"].search_requested.connect(self.search_history)
        self.main_window.views["history"].reprint_requested.connect(self.reprint_invoice)
        self.main_window.views["history"].delete_invoice_requested.connect(self.delete_invoice)

        # Settings View Signals
        self.main_window.views["settings"].save_settings_requested.connect(self.save_settings)
        self.main_window.views["settings"].backup_db_requested.connect(self.backup_database)
        self.main_window.views["settings"].restore_db_requested.connect(self.restore_database)
        self.main_window.views["settings"].theme_change_requested.connect(self.change_theme_from_combo)

    # --- Navigation Logic ---

    def on_page_changed(self, key):
        """Trigger reload actions when switching tabs."""
        logger.info(f"Navigated to page: {key}")
        
        # Set central layout page show
        self.main_window.show_view(self.main_window.views[key])

        if key == "dashboard":
            self.refresh_dashboard()
        elif key == "patient_reg" or key == "patient_rec":
            self.load_patients_list()
            if key == "patient_reg":
                doctors = Doctor.get_active_doctors()
                self.main_window.views["patient_reg"].load_doctors(doctors)
        elif key == "doctors":
            self.load_doctors_list()
        elif key == "procedures":
            self.load_procedures_list()
        elif key == "lab_tests":
            self.load_lab_tests_list()
        elif key == "billing":
            self.billing_ctrl.load_dropdown_data()
            self.main_window.views["billing"].reset_billing()
        elif key == "history":
            self.load_invoice_history()
        elif key == "reports":
            # Populate active tab details initially
            start, end = self.main_window.views["reports"].get_selected_dates_str()
            report_type = self.main_window.views["reports"].get_current_report_type()
            self.reports_ctrl.generate_report(report_type, start, end)
        elif key == "settings":
            self.load_settings_into_view()

    # --- Theme Operations ---

    def on_theme_toggled(self, is_dark):
        self.is_dark = is_dark
        # Update styling inside sub-views
        for view in self.main_window.views.values():
            if hasattr(view, "set_theme"):
                view.set_theme(is_dark)
        
        # Save theme value in DB settings
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                theme_str = "Dark" if is_dark else "Light"
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('theme', ?);", (theme_str,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save theme in settings: {str(e)}")

    def change_theme_from_combo(self, is_dark):
        if is_dark != self.is_dark:
            # Trigger main window toggler to sync sidebar button
            self.main_window.theme_btn.click()

    # --- Dashboard Loading ---

    def refresh_dashboard(self):
        try:
            total_patients = Patient.get_total_count()
            total_doctors = Doctor.get_total_count()
            today_rev = Bill.get_today_revenue()
            today_bills = Bill.get_today_bills_count()
            total_labs = LabTest.get_total_count()

            self.main_window.views["dashboard"].update_metrics(
                total_patients, total_doctors, today_rev, today_bills, total_labs
            )

            # Load charts data (Past 7 days)
            rev_data = Bill.get_daily_revenue_chart_data(7)
            reg_data = Bill.get_daily_registrations_chart_data(7)

            rev_dates = [r[0] for r in rev_data]
            rev_values = [r[1] for r in rev_data]

            reg_dates = [r[0] for r in reg_data]
            reg_values = [r[1] for r in reg_data]

            self.main_window.views["dashboard"].update_charts(
                rev_dates, rev_values, reg_dates, reg_values
            )

            # Load today's invoices
            today_str = datetime.now().strftime("%Y-%m-%d")
            today_pattern = f"{today_str}%"
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT b.*, p.patient_name
                    FROM bills b
                    JOIN patients p ON b.patient_id = p.patient_id
                    WHERE b.created_date LIKE ?
                    ORDER BY b.bill_id DESC;
                """, (today_pattern,))
                rows = cursor.fetchall()
                invoices = [dict(row) for row in rows]
                self.main_window.views["dashboard"].populate_recent_invoices(invoices)

        except Exception as e:
            logger.error(f"Error refreshing dashboard: {str(e)}")

    # --- Patients CRUD ---

    def load_patients_list(self):
        try:
            patients = Patient.get_all_patients()
            self.main_window.views["patient_reg"].populate_patients(patients)
            self.main_window.views["patient_rec"].populate_patients(patients)
        except Exception as e:
            logger.error(f"Error loading patients: {str(e)}")

    def search_patients(self, text):
        try:
            results = Patient.search_patients(text)
            self.main_window.views["patient_reg"].populate_patients(results)
        except Exception as e:
            logger.error(f"Search patients error: {str(e)}")

    def search_patients_rec(self, text):
        try:
            results = Patient.search_patients(text)
            self.main_window.views["patient_rec"].populate_patients(results)
        except Exception as e:
            logger.error(f"Search patients rec error: {str(e)}")

    def add_patient(self, data):
        res = Patient.add_patient(
            name=data["patient_name"],
            father_name=data["father_name"],
            gender=data["gender"],
            age=data["age"],
            phone=data["phone"],
            cnic=data["cnic"],
            address=data["address"]
        )
        if res:
            ToastNotification.show_success(f"Registered patient successfully! ID: {res}", self.main_window)
            self.load_patients_list()
            self.main_window.views["patient_reg"].clear_form()
        else:
            ToastNotification.show_error("Failed to register patient.", self.main_window)

    def update_patient(self, patient_id, data):
        res = Patient.update_patient(
            patient_id=patient_id,
            name=data["patient_name"],
            father_name=data["father_name"],
            gender=data["gender"],
            age=data["age"],
            phone=data["phone"],
            cnic=data["cnic"],
            address=data["address"]
        )
        if res:
            ToastNotification.show_success("Details updated successfully.", self.main_window)
            self.load_patients_list()
            self.main_window.views["patient_reg"].clear_form()
        else:
            ToastNotification.show_error("Failed to update details.", self.main_window)

    def update_patient_rec(self, patient_id, data):
        # Linked from Records view edit form
        res = Patient.update_patient(patient_id, data["patient_name"], data["father_name"], data["gender"], data["age"], data["phone"], data["cnic"], data["address"])
        if res:
            ToastNotification.show_success("Details updated successfully.", self.main_window)
            self.load_patients_list()
            self.main_window.views["patient_rec"].clear_form()
        else:
            ToastNotification.show_error("Failed to update details.", self.main_window)

    def delete_patient(self, patient_id):
        res = Patient.delete_patient(patient_id)
        if res:
            ToastNotification.show_success(f"Patient {patient_id} deleted.", self.main_window)
            self.load_patients_list()
            self.main_window.views["patient_reg"].clear_form()
        else:
            ToastNotification.show_error("Could not delete record (Patient may have billing history).", self.main_window)

    def print_patient_slip(self, data):
        """Registers a patient if new, and displays the QPrintPreviewDialog for the patient slip."""
        patient_id = data.get("patient_id")
        
        if not patient_id:
            # Register patient first
            patient_id = Patient.add_patient(
                name=data["patient_name"],
                father_name=data["father_name"],
                gender=data["gender"],
                age=data["age"],
                phone=data["phone"],
                cnic=data["cnic"],
                address=data["address"]
            )
            if patient_id:
                data["patient_id"] = patient_id
                ToastNotification.show_success(f"Registered patient successfully! ID: {patient_id}", self.main_window)
                self.load_patients_list()
                
                # Update UI form state to Edit mode for this patient
                reg_view = self.main_window.views["patient_reg"]
                reg_view.switch_to_edit_mode(patient_id)
            else:
                ToastNotification.show_error("Failed to register patient for print.", self.main_window)
                return

        # Open the print preview dialog
        doctor = data.get("doctor")
        PrinterManager.preview_patient_slip(data, doctor, self.main_window)

    def delete_patient_rec(self, patient_id):
        res = Patient.delete_patient(patient_id)
        if res:
            ToastNotification.show_success(f"Patient {patient_id} deleted.", self.main_window)
            self.load_patients_list()
            self.main_window.views["patient_rec"].clear_form()
        else:
            ToastNotification.show_error("Could not delete record.", self.main_window)

    # --- Doctors CRUD ---

    def load_doctors_list(self):
        doctors = Doctor.get_all_doctors()
        self.main_window.views["doctors"].populate_doctors(doctors)

    def add_doctor(self, data):
        res = Doctor.add_doctor(data["doctor_name"], data["specialization"], data["consultation_fee"], data["status"])
        if res:
            ToastNotification.show_success("Doctor details saved.", self.main_window)
            self.load_doctors_list()
            self.main_window.views["doctors"].clear_form()
        else:
            ToastNotification.show_error("Failed to save doctor record.", self.main_window)

    def update_doctor(self, doctor_id, data):
        res = Doctor.update_doctor(doctor_id, data["doctor_name"], data["specialization"], data["consultation_fee"], data["status"])
        if res:
            ToastNotification.show_success("Doctor details updated.", self.main_window)
            self.load_doctors_list()
            self.main_window.views["doctors"].clear_form()
        else:
            ToastNotification.show_error("Failed to update doctor record.", self.main_window)

    def delete_doctor(self, doctor_id):
        res = Doctor.delete_doctor(doctor_id)
        if res:
            ToastNotification.show_success("Doctor deleted successfully.", self.main_window)
            self.load_doctors_list()
            self.main_window.views["doctors"].clear_form()
        else:
            ToastNotification.show_error("Failed to delete record.", self.main_window)

    # --- Procedures CRUD ---

    def load_procedures_list(self):
        procedures = Procedure.get_all_procedures()
        self.main_window.views["procedures"].populate_procedures(procedures)

    def add_procedure(self, data):
        res = Procedure.add_procedure(data["procedure_name"], data["category"], data["procedure_fee"])
        if res:
            ToastNotification.show_success("Procedure details saved.", self.main_window)
            self.load_procedures_list()
            self.main_window.views["procedures"].clear_form()
        else:
            ToastNotification.show_error("Failed to save procedure.", self.main_window)

    def update_procedure(self, procedure_id, data):
        res = Procedure.update_procedure(procedure_id, data["procedure_name"], data["category"], data["procedure_fee"])
        if res:
            ToastNotification.show_success("Procedure details updated.", self.main_window)
            self.load_procedures_list()
            self.main_window.views["procedures"].clear_form()
        else:
            ToastNotification.show_error("Failed to update procedure.", self.main_window)

    def delete_procedure(self, procedure_id):
        res = Procedure.delete_procedure(procedure_id)
        if res:
            ToastNotification.show_success("Procedure deleted successfully.", self.main_window)
            self.load_procedures_list()
            self.main_window.views["procedures"].clear_form()
        else:
            ToastNotification.show_error("Failed to delete procedure.", self.main_window)

    # --- Lab Tests CRUD ---

    def load_lab_tests_list(self):
        lab_tests = LabTest.get_all_lab_tests()
        self.main_window.views["lab_tests"].populate_lab_tests(lab_tests)

    def add_lab_test(self, data):
        res = LabTest.add_lab_test(data["test_name"], data["test_fee"])
        if res:
            ToastNotification.show_success("Lab test details saved.", self.main_window)
            self.load_lab_tests_list()
            self.main_window.views["lab_tests"].clear_form()
        else:
            ToastNotification.show_error("Failed to save lab test.", self.main_window)

    def update_lab_test(self, test_id, data):
        res = LabTest.update_lab_test(test_id, data["test_name"], data["test_fee"])
        if res:
            ToastNotification.show_success("Lab test details updated.", self.main_window)
            self.load_lab_tests_list()
            self.main_window.views["lab_tests"].clear_form()
        else:
            ToastNotification.show_error("Failed to update lab test.", self.main_window)

    def delete_lab_test(self, test_id):
        res = LabTest.delete_lab_test(test_id)
        if res:
            ToastNotification.show_success("Lab test deleted successfully.", self.main_window)
            self.load_lab_tests_list()
            self.main_window.views["lab_tests"].clear_form()
        else:
            ToastNotification.show_error("Failed to delete record.", self.main_window)

    # --- Invoice History ---

    def load_invoice_history(self):
        bills = Bill.get_all_bills()
        self.main_window.views["history"].populate_history(bills)

    def search_history(self, text):
        results = Bill.search_bills(text)
        self.main_window.views["history"].populate_history(results)

    def reprint_invoice(self, invoice_number):
        try:
            full_bill = Bill.get_bill_by_invoice(invoice_number)
            if full_bill:
                # Open print preview dialog
                PrinterManager.preview_invoice(full_bill, self.main_window)
            else:
                ToastNotification.show_error("Invoice details not found.", self.main_window)
        except Exception as e:
            logger.error(f"Reprint invoice failed: {str(e)}")

    def delete_invoice(self, bill_id):
        res = Bill.delete_bill(bill_id)
        if res:
            ToastNotification.show_success("Invoice deleted successfully.", self.main_window)
            self.load_invoice_history()
        else:
            ToastNotification.show_error("Failed to delete invoice.", self.main_window)

    # --- Settings & Profile Operations ---

    def load_settings_into_view(self):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings;")
                settings = {row[0]: row[1] for row in cursor.fetchall()}
                self.main_window.views["settings"].load_settings(settings)
        except Exception as e:
            logger.error(f"Failed to load settings: {str(e)}")

    def load_global_settings(self):
        """Applies saved settings during application boot (like theme)."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = 'theme';")
                row = cursor.fetchone()
                if row:
                    theme_val = row[0]
                    self.is_dark = (theme_val == "Dark")
                    self.main_window.is_dark = self.is_dark
                    self.main_window.apply_theme_styling()
                    # Trigger styling updates inside view stacks
                    for view in self.main_window.views.values():
                        if hasattr(view, "set_theme"):
                            view.set_theme(self.is_dark)
        except Exception as e:
            logger.error(f"Failed to load theme boot setting: {str(e)}")

    def save_settings(self, settings_dict):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                for key, val in settings_dict.items():
                    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?);", (key, val))
                conn.commit()
            ToastNotification.show_success("Profile settings updated successfully.", self.main_window)
        except Exception as e:
            logger.error(f"Failed to save settings: {str(e)}")
            ToastNotification.show_error("Failed to update profile settings.", self.main_window)

    def backup_database(self, file_path):
        if self.db.backup_database(file_path):
            ToastNotification.show_success("Database backup created successfully.", self.main_window)
        else:
            ToastNotification.show_error("Failed to create database backup.", self.main_window)

    def restore_database(self, file_path):
        if self.db.restore_database(file_path):
            ToastNotification.show_success("Database restored successfully. Reloading view data...", self.main_window)
            self.refresh_dashboard()
            self.load_patients_list()
        else:
            ToastNotification.show_error("Failed to restore database from backup.", self.main_window)
