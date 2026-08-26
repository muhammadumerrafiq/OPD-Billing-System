from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QDoubleSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from config import AppConfig
from views.widgets.toast import ToastNotification

class LabTestView(QWidget):
    add_requested = pyqtSignal(dict)
    update_requested = pyqtSignal(int, dict)
    delete_requested = pyqtSignal(int)

    def __init__(self, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark_mode
        self.selected_test_id = None

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
        self.form_title = QLabel("Add New Lab Test")
        self.form_title.setFont(QFont("Outfit", 13, QFont.Weight.Bold))
        self.form_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        form_layout.addWidget(self.form_title)
        form_layout.addSpacing(5)

        # Name
        form_layout.addWidget(QLabel("Lab Test Name *"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. CBC, Liver Function Test")
        form_layout.addWidget(self.name_input)

        # Fee
        form_layout.addWidget(QLabel("Test Fee (Rs) *"))
        self.fee_spin = QDoubleSpinBox()
        self.fee_spin.setRange(0, 500000)
        self.fee_spin.setSingleStep(50)
        self.fee_spin.setValue(1000)
        form_layout.addWidget(self.fee_spin)

        form_layout.addSpacing(15)

        # Action Buttons
        self.save_btn = QPushButton("Add Lab Test")
        self.save_btn.setObjectName("BtnSuccess")
        self.save_btn.setMinimumHeight(38)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.on_save_clicked)
        form_layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Delete Lab Test")
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

        self.table_title = QLabel("All Laboratory Tests")
        self.table_title.setFont(QFont("Outfit", 12, QFont.Weight.Bold))
        self.table_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        records_layout.addWidget(self.table_title)

        # Table Grid
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Test Name", "Test Fee"])
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
        self.selected_test_id = int(self.table.item(row, 0).text())
        
        # Populate Form
        self.name_input.setText(self.table.item(row, 1).text())
        
        fee_str = self.table.item(row, 2).text().replace("₨", "").replace("Rs", "").replace(",", "").strip()
        self.fee_spin.setValue(float(fee_str))

        # Switch to Edit Mode
        self.form_title.setText("Edit Test Details")
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
        self.selected_test_id = None
        self.name_input.clear()
        self.fee_spin.setValue(1000.0)

        # Switch back to Add Mode
        self.form_title.setText("Add New Lab Test")
        self.save_btn.setText("Add Lab Test")
        self.save_btn.setObjectName("BtnSuccess")
        self.save_btn.setStyleSheet("")
        self.delete_btn.setVisible(False)
        self.table.clearSelection()

    def on_save_clicked(self):
        name = self.name_input.text().strip()

        if not name:
            ToastNotification.show_error("Test name is required!", self)
            self.name_input.setFocus()
            return

        test_data = {
            "test_name": name,
            "test_fee": self.fee_spin.value()
        }

        if self.selected_test_id is not None:
            self.update_requested.emit(self.selected_test_id, test_data)
        else:
            self.add_requested.emit(test_data)

    def on_delete_clicked(self):
        if self.selected_test_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this lab test?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.selected_test_id)

    def populate_lab_tests(self, lab_tests_list):
        self.table.setRowCount(0)
        self.table.setRowCount(len(lab_tests_list))
        for row_idx, test in enumerate(lab_tests_list):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(test.get("test_id", ""))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(test.get("test_name", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"Rs {test.get('test_fee', 0.0):,.2f}"))

            self.table.item(row_idx, 2).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
