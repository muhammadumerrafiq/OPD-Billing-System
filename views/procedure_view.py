from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QDoubleSpinBox, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from config import AppConfig
from views.widgets.toast import ToastNotification

class ProcedureView(QWidget):
    add_requested = pyqtSignal(dict)
    update_requested = pyqtSignal(int, dict)
    delete_requested = pyqtSignal(int)

    def __init__(self, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark_mode
        self.selected_procedure_id = None

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
        self.form_title = QLabel("Add New Procedure")
        self.form_title.setFont(QFont("Outfit", 13, QFont.Weight.Bold))
        self.form_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        form_layout.addWidget(self.form_title)
        form_layout.addSpacing(5)

        # Name
        form_layout.addWidget(QLabel("Procedure Name *"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Ear Syringing, HydraFacial")
        form_layout.addWidget(self.name_input)

        # Category Dropdown (with categories like Aesthetic, ENT, General, etc. as requested)
        form_layout.addWidget(QLabel("Category *"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["General", "Aesthetic", "ENT", "Dental", "Orthopedic"])
        self.category_combo.setEditable(True) # Allows custom text entry too
        form_layout.addWidget(self.category_combo)

        # Fee
        form_layout.addWidget(QLabel("Procedure Fee (Rs) *"))
        self.fee_spin = QDoubleSpinBox()
        self.fee_spin.setRange(0, 1000000)
        self.fee_spin.setSingleStep(50)
        self.fee_spin.setValue(500)
        form_layout.addWidget(self.fee_spin)

        form_layout.addSpacing(15)

        # Action Buttons
        self.save_btn = QPushButton("Add Procedure")
        self.save_btn.setObjectName("BtnSuccess")
        self.save_btn.setMinimumHeight(38)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.on_save_clicked)
        form_layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Delete Procedure")
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

        self.table_title = QLabel("All Procedures & Services")
        self.table_title.setFont(QFont("Outfit", 12, QFont.Weight.Bold))
        self.table_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        records_layout.addWidget(self.table_title)

        # Table Grid
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Procedure Name", "Category", "Procedure Fee"])
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
        self.selected_procedure_id = int(self.table.item(row, 0).text())
        
        # Populate Form
        self.name_input.setText(self.table.item(row, 1).text())
        self.category_combo.setCurrentText(self.table.item(row, 2).text())
        
        fee_str = self.table.item(row, 3).text().replace("₨", "").replace("Rs", "").replace(",", "").strip()
        self.fee_spin.setValue(float(fee_str))

        # Switch to Edit Mode
        self.form_title.setText("Edit Procedure Details")
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
        self.selected_procedure_id = None
        self.name_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.fee_spin.setValue(500.0)

        # Switch back to Add Mode
        self.form_title.setText("Add New Procedure")
        self.save_btn.setText("Add Procedure")
        self.save_btn.setObjectName("BtnSuccess")
        self.save_btn.setStyleSheet("")
        self.delete_btn.setVisible(False)
        self.table.clearSelection()

    def on_save_clicked(self):
        name = self.name_input.text().strip()
        category = self.category_combo.currentText().strip()

        if not name:
            ToastNotification.show_error("Procedure name is required!", self)
            self.name_input.setFocus()
            return
        if not category:
            ToastNotification.show_error("Category is required!", self)
            self.category_combo.setFocus()
            return

        proc_data = {
            "procedure_name": name,
            "category": category,
            "procedure_fee": self.fee_spin.value()
        }

        if self.selected_procedure_id is not None:
            self.update_requested.emit(self.selected_procedure_id, proc_data)
        else:
            self.add_requested.emit(proc_data)

    def on_delete_clicked(self):
        if self.selected_procedure_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this procedure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.selected_procedure_id)

    def populate_procedures(self, procedures_list):
        self.table.setRowCount(0)
        self.table.setRowCount(len(procedures_list))
        for row_idx, proc in enumerate(procedures_list):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(proc.get("procedure_id", ""))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(proc.get("procedure_name", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(proc.get("category", "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"Rs {proc.get('procedure_fee', 0.0):,.2f}"))

            self.table.item(row_idx, 3).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
