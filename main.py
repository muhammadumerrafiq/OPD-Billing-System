import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from utils.logger import logger
from database.db_manager import DatabaseManager
from models.user import User
from views.login_view import LoginView
from views.main_window import MainWindow
from views.dashboard_view import DashboardView
from views.patient_view import PatientView
from views.patient_records_view import PatientRecordsView
from views.doctor_view import DoctorView
from views.procedure_view import ProcedureView
from views.lab_test_view import LabTestView
from views.billing_view import BillingView
from views.history_view import InvoiceHistoryView
from views.reports_view import ReportsView
from views.settings_view import SettingsView
from controllers.main_controller import MainController
from views.widgets.toast import ToastNotification

class AppCoordinator:
    def __init__(self):
        # Database setup
        self.db = DatabaseManager()
        
        # State management
        self.current_user = None
        self.login_window = None
        self.main_window = None
        self.controller = None
        self.is_dark = False

        # Load initial config settings (theme preference)
        self.load_initial_theme()

        # Show Login Page
        self.show_login()

    def load_initial_theme(self):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = 'theme';")
                row = cursor.fetchone()
                if row:
                    self.is_dark = (row[0] == "Dark")
        except Exception as e:
            logger.error(f"Failed to read initial theme: {str(e)}")

    def show_login(self):
        # Close main window if open
        if self.main_window:
            self.main_window.close()
            self.main_window = None
            self.controller = None

        self.login_window = LoginView(is_dark_mode=self.is_dark)
        self.login_window.login_submitted.connect(self.authenticate_user)
        self.login_window.setWindowTitle("Login - Bismel Medical Center")
        self.login_window.resize(450, 550)
        self.login_window.show()

    def authenticate_user(self, username, password):
        user = User.authenticate(username, password)
        if user:
            self.current_user = user
            self.login_window.close()
            self.login_window = None
            self.show_main_app()
        else:
            ToastNotification.show_error("Invalid username or password.", self.login_window)
            self.login_window.clear_inputs()

    def show_main_app(self):
        # Initialize MainWindow shell
        self.main_window = MainWindow(current_user=self.current_user, is_dark_mode=self.is_dark)
        
        # Instantiate sub-views and map them inside MainWindow's registry
        self.main_window.views = {
            "dashboard": DashboardView(is_dark_mode=self.is_dark, parent=self.main_window),
            "patient_reg": PatientView(is_dark_mode=self.is_dark, parent=self.main_window),
            "patient_rec": PatientRecordsView(current_user=self.current_user, is_dark_mode=self.is_dark, parent=self.main_window),
            "doctors": DoctorView(is_dark_mode=self.is_dark, parent=self.main_window),
            "procedures": ProcedureView(is_dark_mode=self.is_dark, parent=self.main_window),
            "lab_tests": LabTestView(is_dark_mode=self.is_dark, parent=self.main_window),
            "billing": BillingView(is_dark_mode=self.is_dark, parent=self.main_window),
            "history": InvoiceHistoryView(current_user=self.current_user, is_dark_mode=self.is_dark, parent=self.main_window),
            "reports": ReportsView(is_dark_mode=self.is_dark, parent=self.main_window),
            "settings": SettingsView(is_dark_mode=self.is_dark, parent=self.main_window)
        }

        # Add all views to QStackedWidget in main window shell
        for key, widget in self.main_window.views.items():
            self.main_window.register_view(key, widget)

        # Instantiate Main Controller to bind actions
        self.controller = MainController(self.main_window, is_dark_mode=self.is_dark)

        # Set initial stack page and show
        self.main_window.navigate_to_page("dashboard")
        self.main_window.logout_requested.connect(self.logout)
        
        self.main_window.show()
        ToastNotification.show_success(f"Welcome back, {self.current_user.full_name}!", self.main_window)

    def logout(self):
        logger.info(f"User {self.current_user.username} logged out.")
        self.current_user = None
        self.show_login()


def exception_hook(exctype, value, tb):
    """Global exception handler to write logs and display error alerts."""
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    logger.critical(f"Unhandled exception encountered:\n{error_msg}")
    
    # Show message box details
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("System Critical Error")
    msg_box.setText("An unexpected runtime exception has occurred in the application. Please check app.log inside logs folder for details.")
    msg_box.setInformativeText(str(value))
    msg_box.setDetailedText(error_msg)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()
    
    sys.exit(1)


def main():
    # Set high-DPI scaling attributes if supported in local version
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    
    # Set global application details
    app.setApplicationName("Bismel Medical Center Billing")
    app.setOrganizationName("Bismel Medical Center")

    # Hook exceptions
    sys.excepthook = exception_hook

    # Initialize app coordination workflow
    coordinator = AppCoordinator()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
