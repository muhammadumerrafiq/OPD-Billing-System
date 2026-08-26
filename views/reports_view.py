from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QDateEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QGridLayout
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from config import AppConfig
from views.widgets.toast import ToastNotification
from views.widgets.svg_icon import SVGIconFactory

class ReportsView(QWidget):
    # Signals
    generate_report_requested = pyqtSignal(str, str, str) # report_type, start_date, end_date
    export_excel_requested = pyqtSignal(str, str, str)
    export_pdf_requested = pyqtSignal(str, str, str)

    def __init__(self, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark_mode
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        # 1. Date Range Selector Toolbar
        self.toolbar = QFrame()
        self.toolbar.setObjectName("ContentPanel")
        
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(15, 12, 15, 12)
        toolbar_layout.setSpacing(15)

        # Date pickers
        toolbar_layout.addWidget(QLabel("<b>Date Range:</b>"))
        
        toolbar_layout.addWidget(QLabel("From:"))
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate().addDays(-30)) # Default to last 30 days
        self.date_start.setMinimumHeight(34)
        toolbar_layout.addWidget(self.date_start)

        toolbar_layout.addWidget(QLabel("To:"))
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setMinimumHeight(34)
        toolbar_layout.addWidget(self.date_end)

        # Run Button
        self.btn_run = QPushButton("Generate Report")
        self.btn_run.setObjectName("BtnOutline")
        self.btn_run.setMinimumHeight(34)
        self.btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_run.clicked.connect(self.on_generate_clicked)
        toolbar_layout.addWidget(self.btn_run)

        # Export Buttons
        toolbar_layout.addSpacing(20)
        
        self.btn_excel = QPushButton("Export Excel")
        self.btn_excel.setObjectName("BtnOutline")
        self.btn_excel.setMinimumHeight(34)
        self.btn_excel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_excel.clicked.connect(self.on_export_excel)
        toolbar_layout.addWidget(self.btn_excel)

        self.btn_pdf = QPushButton("Export PDF")
        self.btn_pdf.setObjectName("BtnOutline")
        self.btn_pdf.setMinimumHeight(34)
        self.btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pdf.clicked.connect(self.on_export_pdf)
        toolbar_layout.addWidget(self.btn_pdf)

        main_layout.addWidget(self.toolbar)

        # 2. Tabs Widget for different report summaries
        self.tabs = QTabWidget()
        self.tabs.setObjectName("ReportsTabWidget")
        
        # We will create tables for each report category
        # A. General Revenue Summary
        self.tab_revenue = QWidget()
        rev_vbox = QVBoxLayout(self.tab_revenue)
        rev_vbox.setContentsMargins(15, 15, 15, 15)
        
        # Summary totals row
        self.summary_widget = QFrame()
        self.summary_widget.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 108, 189, 0.05);
                border: 1.5px solid #0F6CBD;
                border-radius: 8px;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        sum_grid = QHBoxLayout(self.summary_widget)
        self.lbl_sum_bills = QLabel("<b>Invoices Generated:</b> 0")
        self.lbl_sum_revenue = QLabel("<b>Net Revenue:</b> Rs 0.00")
        self.lbl_sum_discounts = QLabel("<b>Discounts Offered:</b> Rs 0.00")
        sum_grid.addWidget(self.lbl_sum_bills)
        sum_grid.addWidget(self.lbl_sum_discounts)
        sum_grid.addWidget(self.lbl_sum_revenue)
        rev_vbox.addWidget(self.summary_widget)
        rev_vbox.addSpacing(10)

        self.table_revenue = QTableWidget()
        self.table_revenue.setColumnCount(5)
        self.table_revenue.setHorizontalHeaderLabels(["Transaction Date", "Invoices Count", "Subtotal Sum", "Discount Sum", "Net Grand Total"])
        self.table_revenue.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_revenue.verticalHeader().setVisible(False)
        self.table_revenue.setShowGrid(False)
        rev_vbox.addWidget(self.table_revenue)
        self.tabs.addTab(self.tab_revenue, "General Revenue")

        # B. Doctor consultations
        self.tab_doctors = QWidget()
        doc_vbox = QVBoxLayout(self.tab_doctors)
        doc_vbox.setContentsMargins(15, 15, 15, 15)
        self.table_doctors = QTableWidget()
        self.table_doctors.setColumnCount(3)
        self.table_doctors.setHorizontalHeaderLabels(["Doctor Name", "Consultations Count", "Total Revenue"])
        self.table_doctors.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_doctors.verticalHeader().setVisible(False)
        self.table_doctors.setShowGrid(False)
        doc_vbox.addWidget(self.table_doctors)
        self.tabs.addTab(self.tab_doctors, "Doctor-wise Revenue")

        # C. Procedure revenue
        self.tab_procedures = QWidget()
        proc_vbox = QVBoxLayout(self.tab_procedures)
        proc_vbox.setContentsMargins(15, 15, 15, 15)
        self.table_procedures = QTableWidget()
        self.table_procedures.setColumnCount(4)
        self.table_procedures.setHorizontalHeaderLabels(["Procedure Name", "Category", "Quantity Performed", "Total Revenue"])
        self.table_procedures.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_procedures.verticalHeader().setVisible(False)
        self.table_procedures.setShowGrid(False)
        proc_vbox.addWidget(self.table_procedures)
        self.tabs.addTab(self.tab_procedures, "Procedure-wise Revenue")

        # D. Lab test revenue
        self.tab_labs = QWidget()
        lab_vbox = QVBoxLayout(self.tab_labs)
        lab_vbox.setContentsMargins(15, 15, 15, 15)
        self.table_labs = QTableWidget()
        self.table_labs.setColumnCount(3)
        self.table_labs.setHorizontalHeaderLabels(["Lab Test Name", "Quantity Performed", "Total Revenue"])
        self.table_labs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_labs.verticalHeader().setVisible(False)
        self.table_labs.setShowGrid(False)
        lab_vbox.addWidget(self.table_labs)
        self.tabs.addTab(self.tab_labs, "Laboratory Revenue")

        # E. Registrations List
        self.tab_registrations = QWidget()
        reg_vbox = QVBoxLayout(self.tab_registrations)
        reg_vbox.setContentsMargins(15, 15, 15, 15)
        self.table_registrations = QTableWidget()
        self.table_registrations.setColumnCount(6)
        self.table_registrations.setHorizontalHeaderLabels(["Patient ID", "Patient Name", "Gender", "Age", "Phone", "Reg Date"])
        self.table_registrations.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_registrations.verticalHeader().setVisible(False)
        self.table_registrations.setShowGrid(False)
        reg_vbox.addWidget(self.table_registrations)
        self.tabs.addTab(self.tab_registrations, "Patient Registrations")

        main_layout.addWidget(self.tabs, 1)

        self.apply_theme_styling()

    def apply_theme_styling(self):
        self.setStyleSheet(AppConfig.get_stylesheet(self.is_dark))
        
        border_color = AppConfig.COLOR_DARK_BORDER if self.is_dark else AppConfig.COLOR_LIGHT_BORDER
        card_bg = AppConfig.COLOR_DARK_CARD if self.is_dark else AppConfig.COLOR_LIGHT_CARD
        
        self.toolbar.setStyleSheet(f"""
            QFrame#ContentPanel {{
                background-color: {card_bg};
                border: 1.5px solid {border_color};
                border-radius: 12px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

        # Button Icons
        run_pix = SVGIconFactory.get_icon("refresh", color=AppConfig.COLOR_PRIMARY, size=(16, 16))
        self.btn_run.setIcon(run_pix)

        excel_pix = SVGIconFactory.get_icon("save", color=AppConfig.COLOR_PRIMARY, size=(16, 16))
        self.btn_excel.setIcon(excel_pix)

        pdf_pix = SVGIconFactory.get_icon("pdf", color=AppConfig.COLOR_PRIMARY, size=(16, 16))
        self.btn_pdf.setIcon(pdf_pix)

    def set_theme(self, is_dark):
        self.is_dark = is_dark
        self.apply_theme_styling()

    def get_selected_dates_str(self):
        """Returns start_date, end_date as ISO strings (YYYY-MM-DD)."""
        start = self.date_start.date().toString("yyyy-MM-dd")
        end = self.date_end.date().toString("yyyy-MM-dd")
        return start, end

    def get_current_report_type(self):
        """Maps active tab index to report type string."""
        mapping = {
            0: "general_revenue",
            1: "doctor_revenue",
            2: "procedure_revenue",
            3: "lab_revenue",
            4: "patient_registrations"
        }
        return mapping.get(self.tabs.currentIndex(), "general_revenue")

    def on_generate_clicked(self):
        report_type = self.get_current_report_type()
        start, end = self.get_selected_dates_str()
        self.generate_report_requested.emit(report_type, start, end)

    def on_export_excel(self):
        report_type = self.get_current_report_type()
        start, end = self.get_selected_dates_str()
        self.export_excel_requested.emit(report_type, start, end)

    def on_export_pdf(self):
        report_type = self.get_current_report_type()
        start, end = self.get_selected_dates_str()
        self.export_pdf_requested.emit(report_type, start, end)

    # --- Data Population Methods ---

    def populate_general_revenue(self, data):
        self.table_revenue.setRowCount(0)
        self.table_revenue.setRowCount(len(data))
        
        total_bills = 0
        total_discount = 0.0
        total_revenue = 0.0

        for row_idx, row in enumerate(data):
            t_date = row.get("transaction_date", "")
            cnt = row.get("bills_count", 0)
            sub = row.get("subtotal_sum", 0.0)
            disc = row.get("discount_sum", 0.0)
            grand = row.get("grand_total_sum", 0.0)

            total_bills += cnt
            total_discount += disc
            total_revenue += grand

            self.table_revenue.setItem(row_idx, 0, QTableWidgetItem(t_date))
            self.table_revenue.setItem(row_idx, 1, QTableWidgetItem(str(cnt)))
            self.table_revenue.setItem(row_idx, 2, QTableWidgetItem(f"Rs {sub:,.2f}"))
            self.table_revenue.setItem(row_idx, 3, QTableWidgetItem(f"Rs {disc:,.2f}"))
            self.table_revenue.setItem(row_idx, 4, QTableWidgetItem(f"Rs {grand:,.2f}"))

            # Alignments
            self.table_revenue.item(row_idx, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_revenue.item(row_idx, 2).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table_revenue.item(row_idx, 3).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table_revenue.item(row_idx, 4).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Update Summary Labels
        self.lbl_sum_bills.setText(f"<b>Invoices Generated:</b> {total_bills}")
        self.lbl_sum_discounts.setText(f"<b>Discounts Offered:</b> Rs {total_discount:,.2f}")
        self.lbl_sum_revenue.setText(f"<b>Net Revenue:</b> Rs {total_revenue:,.2f}")

    def populate_doctor_revenue(self, data):
        self.table_doctors.setRowCount(0)
        self.table_doctors.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            self.table_doctors.setItem(row_idx, 0, QTableWidgetItem(row.get("doctor_name", "")))
            self.table_doctors.setItem(row_idx, 1, QTableWidgetItem(str(row.get("consultation_count", 0))))
            self.table_doctors.setItem(row_idx, 2, QTableWidgetItem(f"Rs {row.get('total_revenue', 0.0):,.2f}"))

            self.table_doctors.item(row_idx, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_doctors.item(row_idx, 2).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def populate_procedure_revenue(self, data):
        self.table_procedures.setRowCount(0)
        self.table_procedures.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            self.table_procedures.setItem(row_idx, 0, QTableWidgetItem(row.get("procedure_name", "")))
            self.table_procedures.setItem(row_idx, 1, QTableWidgetItem(row.get("category", "General")))
            self.table_procedures.setItem(row_idx, 2, QTableWidgetItem(str(row.get("quantity_sold", 0))))
            self.table_procedures.setItem(row_idx, 3, QTableWidgetItem(f"Rs {row.get('total_revenue', 0.0):,.2f}"))

            self.table_procedures.item(row_idx, 2).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_procedures.item(row_idx, 3).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def populate_lab_revenue(self, data):
        self.table_labs.setRowCount(0)
        self.table_labs.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            self.table_labs.setItem(row_idx, 0, QTableWidgetItem(row.get("test_name", "")))
            self.table_labs.setItem(row_idx, 1, QTableWidgetItem(str(row.get("quantity_sold", 0))))
            self.table_labs.setItem(row_idx, 2, QTableWidgetItem(f"Rs {row.get('total_revenue', 0.0):,.2f}"))

            self.table_labs.item(row_idx, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_labs.item(row_idx, 2).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def populate_registrations_report(self, data):
        self.table_registrations.setRowCount(0)
        self.table_registrations.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            self.table_registrations.setItem(row_idx, 0, QTableWidgetItem(row.get("patient_id", "")))
            self.table_registrations.setItem(row_idx, 1, QTableWidgetItem(row.get("patient_name", "")))
            self.table_registrations.setItem(row_idx, 2, QTableWidgetItem(row.get("gender", "")))
            self.table_registrations.setItem(row_idx, 3, QTableWidgetItem(str(row.get("age", ""))))
            self.table_registrations.setItem(row_idx, 4, QTableWidgetItem(row.get("phone", "")))
            self.table_registrations.setItem(row_idx, 5, QTableWidgetItem(row.get("registration_date", "")))

            self.table_registrations.item(row_idx, 0).setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            self.table_registrations.item(row_idx, 3).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
