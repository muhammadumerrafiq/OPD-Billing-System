from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QTextEdit, QPushButton, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from config import AppConfig
from views.widgets.svg_icon import SVGIconFactory
from views.widgets.toast import ToastNotification
from utils.logger import logger

class PatientView(QWidget):
    # Signals to communicate CRUD requests to controller
    register_requested = pyqtSignal(dict)
    update_requested = pyqtSignal(str, dict)
    delete_requested = pyqtSignal(str)
    print_slip_requested = pyqtSignal(dict)

    def __init__(self, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark_mode
        self.selected_patient_id = None # Tracks if we are in Edit mode
        self.current_address = ""
        
        self.setup_ui()

    def setup_ui(self):
        # Main Layout (Split into left form and right records table)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # 1. LEFT FORM PANEL
        self.form_panel = QFrame()
        self.form_panel.setObjectName("ContentPanel")
        self.form_panel.setFixedWidth(340)
        
        form_layout = QVBoxLayout(self.form_panel)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)

        # Form Header
        self.form_title = QLabel("Register New Patient")
        self.form_title.setFont(QFont("Outfit", 13, QFont.Weight.Bold))
        self.form_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        form_layout.addWidget(self.form_title)
        form_layout.addSpacing(5)

        # Form fields
        form_layout.addWidget(QLabel("Patient Name *"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter full name")
        form_layout.addWidget(self.name_input)



        gender_age_layout = QHBoxLayout()
        
        gender_vbox = QVBoxLayout()
        gender_vbox.setSpacing(6)
        gender_vbox.addWidget(QLabel("Gender"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Male", "Female", "Other"])
        gender_vbox.addWidget(self.gender_combo)
        gender_age_layout.addLayout(gender_vbox, 1)

        age_vbox = QVBoxLayout()
        age_vbox.setSpacing(6)
        age_vbox.addWidget(QLabel("Age (Years)"))
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 150)
        self.age_spin.setValue(25)
        age_vbox.addWidget(self.age_spin)
        gender_age_layout.addLayout(age_vbox, 1)

        form_layout.addLayout(gender_age_layout)

        form_layout.addWidget(QLabel("Phone Number *"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("e.g. 03001234567")
        form_layout.addWidget(self.phone_input)



        form_layout.addWidget(QLabel("Consulting Doctor"))
        self.doctor_combo = QComboBox()
        self.doctor_combo.addItem("Select Doctor...", None)
        form_layout.addWidget(self.doctor_combo)

        form_layout.addSpacing(10)

        # Action Buttons Layout
        self.save_btn = QPushButton("Register Patient")
        self.save_btn.setObjectName("BtnSuccess")
        self.save_btn.setMinimumHeight(38)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.on_save_clicked)
        form_layout.addWidget(self.save_btn)

        self.print_btn = QPushButton("Print Patient Slip")
        self.print_btn.setMinimumHeight(38)
        self.print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.print_btn.clicked.connect(self.on_print_clicked)
        form_layout.addWidget(self.print_btn)

        self.delete_btn = QPushButton("Delete Record")
        self.delete_btn.setObjectName("BtnDanger")
        self.delete_btn.setMinimumHeight(38)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setVisible(False) # Only in edit mode
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        form_layout.addWidget(self.delete_btn)

        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.setObjectName("BtnOutline")
        self.clear_btn.setMinimumHeight(38)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_form)
        form_layout.addWidget(self.clear_btn)

        main_layout.addWidget(self.form_panel)

        # 2. RIGHT RECORDS PANEL
        self.records_panel = QFrame()
        self.records_panel.setObjectName("ContentPanel")
        
        records_layout = QVBoxLayout(self.records_panel)
        records_layout.setContentsMargins(20, 20, 20, 20)
        records_layout.setSpacing(15)

        # Search Bar
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search patients by ID, Name, or Phone...")
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_input, 1)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setObjectName("BtnOutline")
        self.refresh_btn.setMinimumHeight(38)
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.on_refresh_clicked)
        search_layout.addWidget(self.refresh_btn)

        records_layout.addLayout(search_layout)

        # Table Grid
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Patient ID", "Name", "Gender", 
            "Age", "Phone", "Address", "Reg Date"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.itemClicked.connect(self.on_table_row_clicked)

        records_layout.addWidget(self.table)
        main_layout.addWidget(self.records_panel, 1)

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
        self.form_panel.setStyleSheet(panel_style)
        self.records_panel.setStyleSheet(panel_style)
        
        self.form_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY}; border: none; background: transparent;")

        # Icons for action buttons
        ref_pix = SVGIconFactory.get_icon("refresh", color=AppConfig.COLOR_PRIMARY if not self.is_dark else AppConfig.COLOR_SECONDARY, size=(16, 16))
        self.refresh_btn.setIcon(ref_pix)

        print_pix = SVGIconFactory.get_icon("print", color="#FFFFFF", size=(16, 16))
        self.print_btn.setIcon(print_pix)

    def set_theme(self, is_dark):
        self.is_dark = is_dark
        self.apply_theme_styling()

    def on_refresh_clicked(self):
        self.search_input.clear()
        # The parent controller should handle reload

    def on_search_text_changed(self):
        # The parent controller should hook into search
        pass

    def on_table_row_clicked(self, item):
        row = item.row()
        self.selected_patient_id = self.table.item(row, 0).text()
        
        # Populate Form
        self.name_input.setText(self.table.item(row, 1).text())
        self.gender_combo.setCurrentText(self.table.item(row, 2).text())
        self.age_spin.setValue(int(self.table.item(row, 3).text()))
        self.phone_input.setText(self.table.item(row, 4).text())
        self.current_address = self.table.item(row, 5).text()
        self.doctor_combo.setCurrentIndex(0)

        # Switch to Edit Mode
        self.switch_to_edit_mode(self.selected_patient_id)

    def switch_to_edit_mode(self, patient_id):
        self.selected_patient_id = patient_id
        self.form_title.setText("Edit Patient Details")
        self.save_btn.setText("Update Details")
        self.save_btn.setObjectName("BtnOutline")
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1.5px solid {AppConfig.COLOR_PRIMARY};
                color: {AppConfig.COLOR_PRIMARY};
                font-weight: bold;
                background-color: transparent;
            }}
            QPushButton:hover {{
                background-color: rgba(15, 108, 189, 0.1);
            }}
        """)
        self.delete_btn.setVisible(True)

    def clear_form(self):
        self.selected_patient_id = None
        self.name_input.clear()
        self.gender_combo.setCurrentIndex(0)
        self.age_spin.setValue(25)
        self.phone_input.clear()
        self.doctor_combo.setCurrentIndex(0)
        self.current_address = ""

        # Switch back to Register Mode
        self.form_title.setText("Register New Patient")
        self.save_btn.setText("Register Patient")
        self.save_btn.setObjectName("BtnSuccess")
        # Apply standard style sheet
        self.save_btn.setStyleSheet("")
        self.delete_btn.setVisible(False)
        self.table.clearSelection()

    def on_save_clicked(self):
        # Validate Inputs
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        
        if not name:
            ToastNotification.show_error("Patient name is required!", self)
            self.name_input.setFocus()
            return
        if not phone:
            ToastNotification.show_error("Phone number is required!", self)
            self.phone_input.setFocus()
            return

        # Prepare details dict
        patient_data = {
            "patient_name": name,
            "father_name": "",
            "gender": self.gender_combo.currentText(),
            "age": self.age_spin.value(),
            "phone": phone,
            "cnic": "",
            "address": self.current_address
        }

        if self.selected_patient_id:
            # Emit Update
            self.update_requested.emit(self.selected_patient_id, patient_data)
        else:
            # Emit Insert
            self.register_requested.emit(patient_data)

    def on_delete_clicked(self):
        if not self.selected_patient_id:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to permanently delete patient {self.selected_patient_id}?\nThis action cannot be undone and will fail if the patient has billing records.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.selected_patient_id)

    def populate_patients(self, patients_list):
        """Populates the records table."""
        self.table.setRowCount(0)
        self.table.setRowCount(len(patients_list))
        for row_idx, pat in enumerate(patients_list):
            self.table.setItem(row_idx, 0, QTableWidgetItem(pat.get("patient_id", "")))
            self.table.setItem(row_idx, 1, QTableWidgetItem(pat.get("patient_name", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(pat.get("gender", "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(pat.get("age", ""))))
            self.table.setItem(row_idx, 4, QTableWidgetItem(pat.get("phone", "")))
            self.table.setItem(row_idx, 5, QTableWidgetItem(pat.get("address", "")))
            self.table.setItem(row_idx, 6, QTableWidgetItem(pat.get("registration_date", "")))

            # Stylize grid values matching alignment
            self.table.item(row_idx, 0).setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))

    def load_doctors(self, doctors_list):
        """Populates the doctor selection combobox without showing fees."""
        # Preserve current selection if possible
        current_data = self.doctor_combo.currentData()
        
        self.doctor_combo.clear()
        self.doctor_combo.addItem("Select Doctor...", None)
        
        select_idx = 0
        for idx, doc in enumerate(doctors_list):
            display = f"{doc['doctor_name']} ({doc['specialization']})"
            self.doctor_combo.addItem(display, doc)
            if current_data and current_data.get('doctor_id') == doc.get('doctor_id'):
                select_idx = idx + 1
        
        self.doctor_combo.setCurrentIndex(select_idx)

    def on_print_clicked(self):
        # Validate Inputs
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        
        if not name:
            ToastNotification.show_error("Patient name is required to print!", self)
            self.name_input.setFocus()
            return
        if not phone:
            ToastNotification.show_error("Phone number is required to print!", self)
            self.phone_input.setFocus()
            return

        # Prepare print details dict
        doctor = self.doctor_combo.currentData()
        
        patient_data = {
            "patient_id": self.selected_patient_id,
            "patient_name": name,
            "father_name": "",
            "gender": self.gender_combo.currentText(),
            "age": self.age_spin.value(),
            "phone": phone,
            "cnic": "",
            "address": self.current_address,
            "doctor": doctor
        }
        
        self.print_slip_requested.emit(patient_data)
