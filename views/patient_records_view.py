from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QComboBox, QSpinBox, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from config import AppConfig
from views.widgets.toast import ToastNotification

class PatientRecordsView(QWidget):
    update_requested = pyqtSignal(str, dict)
    delete_requested = pyqtSignal(str)

    def __init__(self, current_user, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.is_dark = is_dark_mode
        self.selected_patient_id = None
        self.current_address = ""

        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # 1. LEFT FORM PANEL (Details View & Edit Drawer)
        self.details_panel = QFrame()
        self.details_panel.setObjectName("ContentPanel")
        self.details_panel.setFixedWidth(340)
        
        details_layout = QVBoxLayout(self.details_panel)
        details_layout.setContentsMargins(20, 20, 20, 20)
        details_layout.setSpacing(12)

        self.details_title = QLabel("Select a Patient Record")
        self.details_title.setFont(QFont("Outfit", 13, QFont.Weight.Bold))
        self.details_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        details_layout.addWidget(self.details_title)
        details_layout.addSpacing(5)

        # Form fields for editing
        self.editor_widget = QWidget()
        editor_layout = QVBoxLayout(self.editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(10)

        editor_layout.addWidget(QLabel("Patient Name *"))
        self.name_input = QLineEdit()
        editor_layout.addWidget(self.name_input)



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
        age_vbox.addWidget(self.age_spin)
        gender_age_layout.addLayout(age_vbox, 1)

        editor_layout.addLayout(gender_age_layout)

        editor_layout.addWidget(QLabel("Phone Number *"))
        self.phone_input = QLineEdit()
        editor_layout.addWidget(self.phone_input)




        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setObjectName("BtnOutline")
        self.save_btn.setMinimumHeight(38)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.on_save_clicked)
        editor_layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Delete Patient")
        self.delete_btn.setObjectName("BtnDanger")
        self.delete_btn.setMinimumHeight(38)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        editor_layout.addWidget(self.delete_btn)

        self.clear_btn = QPushButton("Cancel")
        self.clear_btn.setObjectName("BtnOutline")
        self.clear_btn.setMinimumHeight(38)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_form)
        editor_layout.addWidget(self.clear_btn)

        details_layout.addWidget(self.editor_widget)
        self.editor_widget.setVisible(False) # Invisible until patient selected

        # Placeholder label when no patient is selected
        self.placeholder_lbl = QLabel("Choose a patient from the records grid on the right to view details or modify their record.")
        self.placeholder_lbl.setWordWrap(True)
        self.placeholder_lbl.setStyleSheet("color: #64748B; font-style: italic;")
        details_layout.addWidget(self.placeholder_lbl)

        main_layout.addWidget(self.details_panel)

        # 2. RIGHT RECORDS PANEL (Search + Full Grid)
        self.records_panel = QFrame()
        self.records_panel.setObjectName("ContentPanel")
        
        records_layout = QVBoxLayout(self.records_panel)
        records_layout.setContentsMargins(20, 20, 20, 20)
        records_layout.setSpacing(15)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search patient archive by ID, Name, or Phone...")
        self.search_input.setMinimumHeight(38)
        records_layout.addWidget(self.search_input)

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
        self.details_panel.setStyleSheet(panel_style)
        self.records_panel.setStyleSheet(panel_style)
        
        self.details_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY}; border: none; background: transparent;")

    def set_theme(self, is_dark):
        self.is_dark = is_dark
        self.apply_theme_styling()

    def on_table_row_clicked(self, item):
        row = item.row()
        self.selected_patient_id = self.table.item(row, 0).text()
        
        # Populate Form
        self.name_input.setText(self.table.item(row, 1).text())
        self.gender_combo.setCurrentText(self.table.item(row, 2).text())
        self.age_spin.setValue(int(self.table.item(row, 3).text()))
        self.phone_input.setText(self.table.item(row, 4).text())
        self.current_address = self.table.item(row, 5).text()

        # Switch details panel text
        self.details_title.setText(f"Details: {self.selected_patient_id}")
        self.placeholder_lbl.setVisible(False)
        self.editor_widget.setVisible(True)

        # Receptionist has delete block
        if self.current_user.role != "Admin":
            self.delete_btn.setVisible(False)

    def clear_form(self):
        self.selected_patient_id = None
        self.current_address = ""
        self.details_title.setText("Select a Patient Record")
        self.editor_widget.setVisible(False)
        self.placeholder_lbl.setVisible(True)
        self.table.clearSelection()

    def on_save_clicked(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not name:
            ToastNotification.show_error("Name is required.", self)
            self.name_input.setFocus()
            return
        if not phone:
            ToastNotification.show_error("Phone is required.", self)
            self.phone_input.setFocus()
            return

        patient_data = {
            "patient_name": name,
            "father_name": "",
            "gender": self.gender_combo.currentText(),
            "age": self.age_spin.value(),
            "phone": phone,
            "cnic": "",
            "address": self.current_address
        }

        self.update_requested.emit(self.selected_patient_id, patient_data)

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

            self.table.item(row_idx, 0).setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        
        self.clear_form()
