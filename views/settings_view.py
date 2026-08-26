from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QTextEdit, QPushButton, QFormLayout, QFileDialog, QMessageBox, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from config import AppConfig
from views.widgets.toast import ToastNotification
from views.widgets.svg_icon import SVGIconFactory

class SettingsView(QWidget):
    # Signals
    save_settings_requested = pyqtSignal(dict)
    backup_db_requested = pyqtSignal(str) # Passes backup filepath
    restore_db_requested = pyqtSignal(str) # Passes restore filepath
    theme_change_requested = pyqtSignal(bool) # True = dark

    def __init__(self, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark_mode
        self.setup_ui()

    def setup_ui(self):
        # Scrollable layout or vertical grid
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # LEFT COLUMN: Hospital Details & Invoice Settings
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)

        # 1. Hospital Info Panel
        self.hospital_panel = QFrame()
        self.hospital_panel.setObjectName("ContentPanel")
        
        hosp_layout = QVBoxLayout(self.hospital_panel)
        hosp_layout.setContentsMargins(20, 20, 20, 20)
        hosp_layout.setSpacing(10)

        hosp_title = QLabel("Hospital Profile Information")
        hosp_title.setFont(QFont("Outfit", 12, QFont.Weight.Bold))
        hosp_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        hosp_layout.addWidget(hosp_title)
        hosp_layout.addSpacing(5)

        form_hosp = QFormLayout()
        form_hosp.setSpacing(10)
        
        self.txt_name = QLineEdit()
        form_hosp.addRow("Hospital Name *", self.txt_name)
        
        self.txt_phone = QLineEdit()
        form_hosp.addRow("Contact Phone *", self.txt_phone)
        
        self.txt_email = QLineEdit()
        form_hosp.addRow("Official Email Address", self.txt_email)
        
        self.txt_address = QTextEdit()
        self.txt_address.setMaximumHeight(60)
        form_hosp.addRow("Hospital Postal Address", self.txt_address)

        hosp_layout.addLayout(form_hosp)
        left_layout.addWidget(self.hospital_panel)

        # 2. Invoice Settings Panel
        self.invoice_panel = QFrame()
        self.invoice_panel.setObjectName("ContentPanel")
        
        inv_layout = QVBoxLayout(self.invoice_panel)
        inv_layout.setContentsMargins(20, 20, 20, 20)
        inv_layout.setSpacing(10)

        inv_title = QLabel("Invoice Rendering Options")
        inv_title.setFont(QFont("Outfit", 12, QFont.Weight.Bold))
        inv_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        inv_layout.addWidget(inv_title)
        inv_layout.addSpacing(5)

        form_inv = QFormLayout()
        form_inv.setSpacing(10)

        self.txt_prefix = QLineEdit()
        self.txt_prefix.setPlaceholderText("e.g. INV")
        self.txt_prefix.setMaxLength(10)
        form_inv.addRow("Invoice Prefix", self.txt_prefix)

        self.txt_footer = QTextEdit()
        self.txt_footer.setPlaceholderText("e.g. Thank You For Visiting Bismel Medical Center")
        self.txt_footer.setMaximumHeight(50)
        form_inv.addRow("Invoice Footer Quote", self.txt_footer)

        inv_layout.addLayout(form_inv)
        left_layout.addWidget(self.invoice_panel)

        main_layout.addLayout(left_layout, 6)

        # RIGHT COLUMN: Backup, Themes, Actions
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)

        # 3. System Theme Settings Panel
        self.theme_panel = QFrame()
        self.theme_panel.setObjectName("ContentPanel")
        
        theme_layout = QVBoxLayout(self.theme_panel)
        theme_layout.setContentsMargins(20, 20, 20, 20)
        theme_layout.setSpacing(12)

        theme_title = QLabel("Theme Personalization")
        theme_title.setFont(QFont("Outfit", 12, QFont.Weight.Bold))
        theme_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        theme_layout.addWidget(theme_title)
        theme_layout.addSpacing(5)

        theme_form = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light Theme", "Dark Theme"])
        # Listen to change
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        theme_form.addRow("Visual Interface Style", self.theme_combo)
        
        theme_layout.addLayout(theme_form)
        right_layout.addWidget(self.theme_panel)

        # 4. Maintenance / Database Utilities
        self.maint_panel = QFrame()
        self.maint_panel.setObjectName("ContentPanel")
        
        maint_layout = QVBoxLayout(self.maint_panel)
        maint_layout.setContentsMargins(20, 20, 20, 20)
        maint_layout.setSpacing(12)

        maint_title = QLabel("Database Maintenance Tools")
        maint_title.setFont(QFont("Outfit", 12, QFont.Weight.Bold))
        maint_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        maint_layout.addWidget(maint_title)
        maint_layout.addSpacing(5)

        # Backup Button
        self.btn_backup = QPushButton("Create Database Backup")
        self.btn_backup.setObjectName("BtnOutline")
        self.btn_backup.setMinimumHeight(38)
        self.btn_backup.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_backup.clicked.connect(self.on_backup_clicked)
        maint_layout.addWidget(self.btn_backup)

        # Restore Button
        self.btn_restore = QPushButton("Restore Database Backup")
        self.btn_restore.setObjectName("BtnDanger")
        self.btn_restore.setMinimumHeight(38)
        self.btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restore.clicked.connect(self.on_restore_clicked)
        maint_layout.addWidget(self.btn_restore)

        right_layout.addWidget(self.maint_panel)

        # Push elements to top, then layout final Save Profile Settings button
        right_layout.addStretch()

        self.btn_save = QPushButton("Save All Profile Changes")
        self.btn_save.setObjectName("BtnSuccess")
        self.btn_save.setMinimumHeight(44)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self.on_save_clicked)
        right_layout.addWidget(self.btn_save)

        main_layout.addLayout(right_layout, 5)

        self.apply_theme_styling()

    def apply_theme_styling(self):
        self.setStyleSheet(AppConfig.get_stylesheet(self.is_dark))
        
        border_color = AppConfig.COLOR_DARK_BORDER if self.is_dark else AppConfig.COLOR_LIGHT_BORDER
        card_bg = AppConfig.COLOR_DARK_CARD if self.is_dark else AppConfig.COLOR_LIGHT_CARD
        
        panel_style = f"""
            QFrame#ContentPanel {{
                background-color: {card_bg};
                border: 1.5px solid {border_color};
                border-radius: 12px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """
        self.hospital_panel.setStyleSheet(panel_style)
        self.invoice_panel.setStyleSheet(panel_style)
        self.theme_panel.setStyleSheet(panel_style)
        self.maint_panel.setStyleSheet(panel_style)

        # Update title colors
        self.theme_combo.setCurrentIndex(1 if self.is_dark else 0)

    def set_theme(self, is_dark):
        self.is_dark = is_dark
        self.apply_theme_styling()

    def load_settings(self, settings_dict):
        self.txt_name.setText(settings_dict.get("hospital_name", ""))
        self.txt_phone.setText(settings_dict.get("hospital_phone", ""))
        self.txt_email.setText(settings_dict.get("hospital_email", ""))
        self.txt_address.setPlainText(settings_dict.get("hospital_address", ""))
        self.txt_prefix.setText(settings_dict.get("invoice_prefix", "INV"))
        self.txt_footer.setPlainText(settings_dict.get("invoice_footer", ""))
        
        theme_val = settings_dict.get("theme", "Light")
        self.theme_combo.setCurrentIndex(1 if theme_val == "Dark" else 0)

    def on_theme_changed(self, index):
        is_dark = (index == 1)
        self.theme_change_requested.emit(is_dark)

    def on_save_clicked(self):
        name = self.txt_name.text().strip()
        phone = self.txt_phone.text().strip()

        if not name:
            ToastNotification.show_error("Hospital Name is required.", self)
            self.txt_name.setFocus()
            return
        if not phone:
            ToastNotification.show_error("Contact Phone is required.", self)
            self.txt_phone.setFocus()
            return

        settings_dict = {
            "hospital_name": name,
            "hospital_phone": phone,
            "hospital_email": self.txt_email.text().strip(),
            "hospital_address": self.txt_address.toPlainText().strip(),
            "invoice_prefix": self.txt_prefix.text().strip(),
            "invoice_footer": self.txt_footer.toPlainText().strip(),
            "theme": "Dark" if self.theme_combo.currentIndex() == 1 else "Light"
        }

        self.save_settings_requested.emit(settings_dict)

    def on_backup_clicked(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Database Backup",
            "opd_billing_backup.db",
            "SQLite Files (*.db)"
        )
        if file_path:
            self.backup_db_requested.emit(file_path)

    def on_restore_clicked(self):
        reply = QMessageBox.warning(
            self,
            "Confirm Database Restore",
            "Restoring database will replace all current patients, doctors, bills, and log records with the backup file.\nAre you sure you want to proceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Database Backup to Restore",
                "",
                "SQLite Files (*.db)"
            )
            if file_path:
                self.restore_db_requested.emit(file_path)
