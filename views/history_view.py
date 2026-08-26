import os
import subprocess
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from config import AppConfig
from views.widgets.toast import ToastNotification
from views.widgets.svg_icon import SVGIconFactory

class InvoiceHistoryView(QWidget):
    search_requested = pyqtSignal(str)
    reprint_requested = pyqtSignal(str)
    delete_invoice_requested = pyqtSignal(int) # passes bill_id

    def __init__(self, current_user, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.is_dark = is_dark_mode
        self.selected_invoice = None # Dict containing row info

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # Container
        self.container = QFrame()
        self.container.setObjectName("ContentPanel")
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)

        # Title & Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search history by Patient Name, Invoice Number or ID...")
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(self.on_search_changed)
        toolbar_layout.addWidget(self.search_input, 1)

        self.btn_open_pdf = QPushButton("View PDF")
        self.btn_open_pdf.setObjectName("BtnOutline")
        self.btn_open_pdf.setMinimumHeight(38)
        self.btn_open_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_pdf.setEnabled(False)
        self.btn_open_pdf.clicked.connect(self.on_open_pdf_clicked)
        toolbar_layout.addWidget(self.btn_open_pdf)

        self.btn_print = QPushButton("Reprint")
        self.btn_print.setObjectName("BtnOutline")
        self.btn_print.setMinimumHeight(38)
        self.btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_print.setEnabled(False)
        self.btn_print.clicked.connect(self.on_reprint_clicked)
        toolbar_layout.addWidget(self.btn_print)

        self.btn_delete = QPushButton("Delete Invoice")
        self.btn_delete.setObjectName("BtnDanger")
        self.btn_delete.setMinimumHeight(38)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self.on_delete_clicked)
        
        # Hide delete for receptionist
        if self.current_user.role != "Admin":
            self.btn_delete.setVisible(False)
            
        toolbar_layout.addWidget(self.btn_delete)
        container_layout.addLayout(toolbar_layout)

        # Table Grid
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Invoice Number", "Patient ID", "Patient Name", "Created Date", "Grand Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.itemClicked.connect(self.on_table_row_clicked)

        container_layout.addWidget(self.table)
        main_layout.addWidget(self.container)

        self.apply_theme_styling()

    def apply_theme_styling(self):
        self.setStyleSheet(AppConfig.get_stylesheet(self.is_dark))
        
        border_color = AppConfig.COLOR_DARK_BORDER if self.is_dark else AppConfig.COLOR_LIGHT_BORDER
        card_bg = AppConfig.COLOR_DARK_CARD if self.is_dark else AppConfig.COLOR_LIGHT_CARD
        
        self.container.setStyleSheet(f"""
            QFrame#ContentPanel {{
                background-color: {card_bg};
                border: 1.5px solid {border_color};
                border-radius: 12px;
            }}
        """)

        # Button icons
        pdf_icon = SVGIconFactory.get_icon("pdf", color=AppConfig.COLOR_PRIMARY, size=(16, 16))
        self.btn_open_pdf.setIcon(pdf_icon)
        
        print_icon = SVGIconFactory.get_icon("print", color=AppConfig.COLOR_PRIMARY, size=(16, 16))
        self.btn_print.setIcon(print_icon)

    def set_theme(self, is_dark):
        self.is_dark = is_dark
        self.apply_theme_styling()

    def on_search_changed(self):
        query = self.search_input.text().strip()
        self.search_requested.emit(query)

    def on_table_row_clicked(self, item):
        row = item.row()
        self.selected_invoice = {
            "bill_id": int(self.table.item(row, 0).text()),
            "invoice_number": self.table.item(row, 1).text(),
            "patient_id": self.table.item(row, 2).text(),
            "patient_name": self.table.item(row, 3).text(),
            "created_date": self.table.item(row, 4).text()
        }

        # Enable buttons
        self.btn_open_pdf.setEnabled(True)
        self.btn_print.setEnabled(True)
        self.btn_delete.setEnabled(True)

    def clear_selection(self):
        self.selected_invoice = None
        self.btn_open_pdf.setEnabled(False)
        self.btn_print.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.table.clearSelection()

    def on_open_pdf_clicked(self):
        if not self.selected_invoice:
            return
        
        # Invoices naming format: INV-YYYY-XXXXX.pdf under project root/Invoices
        import sys
        if getattr(sys, 'frozen', False):
            project_dir = os.path.dirname(sys.executable)
        else:
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pdf_path = os.path.join(project_dir, "Invoices", f"{self.selected_invoice['invoice_number']}.pdf")

        if os.path.exists(pdf_path):
            try:
                # Open PDF with OS default application
                os.startfile(pdf_path)
            except Exception as e:
                ToastNotification.show_error(f"Cannot open PDF: {str(e)}", self)
        else:
            ToastNotification.show_error("PDF invoice file not found. Please reprint to regenerate.", self)

    def on_reprint_clicked(self):
        if self.selected_invoice:
            self.reprint_requested.emit(self.selected_invoice["invoice_number"])

    def on_delete_clicked(self):
        if not self.selected_invoice:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete invoice {self.selected_invoice['invoice_number']}?\nThis will remove it from database logs.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_invoice_requested.emit(self.selected_invoice["bill_id"])

    def populate_history(self, bills_list):
        self.table.setRowCount(0)
        self.table.setRowCount(len(bills_list))
        for row_idx, bill in enumerate(bills_list):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(bill.get("bill_id", ""))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(bill.get("invoice_number", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(bill.get("patient_id", "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(bill.get("patient_name", "")))
            self.table.setItem(row_idx, 4, QTableWidgetItem(bill.get("created_date", "")))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"Rs {bill.get('grand_total', 0.0):,.2f}"))

            self.table.item(row_idx, 1).setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            self.table.item(row_idx, 5).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.clear_selection()
