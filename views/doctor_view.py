from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QDoubleSpinBox, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from config import AppConfig
from views.widgets.toast import ToastNotification
from views.widgets.svg_icon import SVGIconFactory

class DoctorView(QWidget):
    add_requested = pyqtSignal(dict)
    update_requested = pyqtSignal(int, dict)
    delete_requested = pyqtSignal(int)

    def __init__(self, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark_mode
        self.selected_doctor_id = None

        self.setup_ui()

    def setup_ui(self):
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

        # Header
        self.form_title = QLabel("Add New Doctor")
        self.form_title.setFont(QFont("Outfit", 13, QFont.Weight.Bold))
        self.form_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        form_layout.addWidget(self.form_title)
        form_layout.addSpacing(5)

        # Name
        form_layout.addWidget(QLabel("Doctor Name *"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Dr. Muhammad Yasir")
        form_layout.addWidget(self.name_input)

        # Specialization
        form_layout.addWidget(QLabel("Specialization *"))
        self.spec_input = QLineEdit()
        self.spec_input.setPlaceholderText("e.g. ENT Specialist, General Physician")
        form_layout.addWidget(self.spec_input)

        # Consultation Fee
        form_layout.addWidget(QLabel("Consultation Fee (Rs) *"))
        self.fee_spin = QDoubleSpinBox()
        self.fee_spin.setRange(0, 100000)
        self.fee_spin.setSingleStep(100)
        self.fee_spin.setValue(1000)
        form_layout.addWidget(self.fee_spin)

        # Status
        form_layout.addWidget(QLabel("Status"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive"])
        form_layout.addWidget(self.status_combo)

        form_layout.addSpacing(15)

        # Action Buttons
        self.save_btn = QPushButton("Add Doctor")
        self.save_btn.setObjectName("BtnSuccess")
        self.save_btn.setMinimumHeight(38)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.on_save_clicked)
        form_layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Delete Doctor")
        self.delete_btn.setObjectName("BtnDanger")
        self.delete_btn.setMinimumHeight(38)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setVisible(False)
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

        # Search box or header details
        self.table_title = QLabel("All Registered Doctors")
        self.table_title.setFont(QFont("Outfit", 12, QFont.Weight.Bold))
        self.table_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        records_layout.addWidget(self.table_title)

        # Doctors Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Doctor ID", "Doctor Name", "Specialization", "Consultation Fee", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
        self.table_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY}; border: none; background: transparent;")

    def set_theme(self, is_dark):
        self.is_dark = is_dark
        self.apply_theme_styling()

    def on_table_row_clicked(self, item):
        row = item.row()
        self.selected_doctor_id = int(self.table.item(row, 0).text())
        
        # Populate Form
        self.name_input.setText(self.table.item(row, 1).text())
        self.spec_input.setText(self.table.item(row, 2).text())
        
        # Extract fee amount
        fee_str = self.table.item(row, 3).text().replace("₨", "").replace("Rs", "").replace(",", "").strip()
        self.fee_spin.setValue(float(fee_str))
        
        self.status_combo.setCurrentText(self.table.item(row, 4).text())

        # Switch to Edit Mode
        self.form_title.setText("Edit Doctor Details")
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
        self.selected_doctor_id = None
        self.name_input.clear()
        self.spec_input.clear()
        self.fee_spin.setValue(1000.0)
        self.status_combo.setCurrentIndex(0)

        # Switch back to Add Mode
        self.form_title.setText("Add New Doctor")
        self.save_btn.setText("Add Doctor")
        self.save_btn.setObjectName("BtnSuccess")
        self.save_btn.setStyleSheet("")
        self.delete_btn.setVisible(False)
        self.table.clearSelection()

    def on_save_clicked(self):
        name = self.name_input.text().strip()
        spec = self.spec_input.text().strip()

        if not name:
            ToastNotification.show_error("Doctor name is required!", self)
            self.name_input.setFocus()
            return
        if not spec:
            ToastNotification.show_error("Specialization is required!", self)
            self.spec_input.setFocus()
            return

        doc_data = {
            "doctor_name": name,
            "specialization": spec,
            "consultation_fee": self.fee_spin.value(),
            "status": self.status_combo.currentText()
        }

        if self.selected_doctor_id is not None:
            self.update_requested.emit(self.selected_doctor_id, doc_data)
        else:
            self.add_requested.emit(doc_data)

    def on_delete_clicked(self):
        if self.selected_doctor_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this doctor record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.selected_doctor_id)

    def populate_doctors(self, doctors_list):
        self.table.setRowCount(0)
        self.table.setRowCount(len(doctors_list))
        for row_idx, doc in enumerate(doctors_list):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(doc.get("doctor_id", ""))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(doc.get("doctor_name", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(doc.get("specialization", "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"Rs {doc.get('consultation_fee', 0.0):,.2f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(doc.get("status", "")))

            # Format fields
            self.table.item(row_idx, 3).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
