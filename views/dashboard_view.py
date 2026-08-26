from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from views.widgets.cards import MetricCard
from views.widgets.charts import QtChartWidget
from config import AppConfig

class DashboardView(QWidget):
    def __init__(self, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark_mode
        self.cards = {}
        self.setup_ui()

    def setup_ui(self):
        # Main Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(25, 20, 25, 20)
        self.layout.setSpacing(20)

        # 1. Metric Cards Row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        # Create Metric Cards
        self.cards["patients"] = MetricCard("Total Patients", "0", "patients_rec", AppConfig.COLOR_PRIMARY, self)
        self.cards["doctors"] = MetricCard("Total Doctors", "0", "doctors", AppConfig.COLOR_SECONDARY, self)
        self.cards["revenue"] = MetricCard("Today's Revenue", "Rs 0.00", "billing", AppConfig.COLOR_SUCCESS, self)
        self.cards["bills"] = MetricCard("Today's Bills", "0", "history", AppConfig.COLOR_PRIMARY, self)
        self.cards["lab_tests"] = MetricCard("Total Lab Tests", "0", "lab_tests", AppConfig.COLOR_SECONDARY, self)

        for card in self.cards.values():
            cards_layout.addWidget(card)

        self.layout.addLayout(cards_layout)

        # 2. Charts Row (Two charts side by side)
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)

        # Revenue Chart Widget
        self.revenue_chart_container = QFrame()
        self.revenue_chart_container.setObjectName("ContentPanel")
        rev_layout = QVBoxLayout(self.revenue_chart_container)
        rev_layout.setContentsMargins(15, 15, 15, 15)
        self.revenue_chart = QtChartWidget("revenue", self, self.is_dark)
        rev_layout.addWidget(self.revenue_chart)
        charts_layout.addWidget(self.revenue_chart_container, 1)

        # Registrations Chart Widget
        self.reg_chart_container = QFrame()
        self.reg_chart_container.setObjectName("ContentPanel")
        reg_layout = QVBoxLayout(self.reg_chart_container)
        reg_layout.setContentsMargins(15, 15, 15, 15)
        self.reg_chart = QtChartWidget("registrations", self, self.is_dark)
        reg_layout.addWidget(self.reg_chart)
        charts_layout.addWidget(self.reg_chart_container, 1)

        self.layout.addLayout(charts_layout, 1)

        # 3. Recent Invoices Section
        self.table_container = QFrame()
        self.table_container.setObjectName("ContentPanel")
        
        table_layout = QVBoxLayout(self.table_container)
        table_layout.setContentsMargins(20, 15, 20, 15)
        table_layout.setSpacing(10)

        # Section Title
        self.table_title = QLabel("Recent Invoices (Today)")
        self.table_title.setFont(QFont("Outfit", 12, QFont.Weight.Bold))
        self.table_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        table_layout.addWidget(self.table_title)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Invoice Number", "Patient Name", "Created Date", "Grand Total", "Payment Method"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(200)

        table_layout.addWidget(self.table)
        self.layout.addWidget(self.table_container)

        self.apply_theme_styling()

    def apply_theme_styling(self):
        # Style sheet
        self.setStyleSheet(AppConfig.get_stylesheet(self.is_dark))
        
        # Style containers
        border_color = AppConfig.COLOR_DARK_BORDER if self.is_dark else AppConfig.COLOR_LIGHT_BORDER
        card_bg = AppConfig.COLOR_DARK_CARD if self.is_dark else AppConfig.COLOR_LIGHT_CARD
        
        panel_style = f"""
            QFrame#ContentPanel {{
                background-color: {card_bg};
                border: 1.5px solid {border_color};
                border-radius: 12px;
            }}
        """
        self.revenue_chart_container.setStyleSheet(panel_style)
        self.reg_chart_container.setStyleSheet(panel_style)
        self.table_container.setStyleSheet(panel_style)

        text_color = AppConfig.COLOR_DARK_TEXT if self.is_dark else AppConfig.COLOR_LIGHT_TEXT
        self.table_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY}; border: none;")

        # Update cards
        for card in self.cards.values():
            card.update_theme(self.is_dark)

        # Update charts theme
        self.revenue_chart.set_theme(self.is_dark)
        self.reg_chart.set_theme(self.is_dark)

    def set_theme(self, is_dark):
        self.is_dark = is_dark
        self.apply_theme_styling()

    def update_metrics(self, total_patients, total_doctors, today_rev, today_bills, total_labs):
        """Updates the numeric metrics inside cards."""
        self.cards["patients"].set_value(total_patients)
        self.cards["doctors"].set_value(total_doctors)
        self.cards["revenue"].set_value(f"Rs {today_rev:,.2f}")
        self.cards["bills"].set_value(today_bills)
        self.cards["lab_tests"].set_value(total_labs)

    def update_charts(self, revenue_dates, revenue_values, reg_dates, reg_values):
        """Updates both registration and revenue charts."""
        self.revenue_chart.update_data(revenue_dates, revenue_values)
        self.reg_chart.update_data(reg_dates, reg_values)

    def populate_recent_invoices(self, invoices):
        """Populates the recent invoices table."""
        self.table.setRowCount(0)
        self.table.setRowCount(len(invoices))
        for row_idx, inv in enumerate(invoices):
            self.table.setItem(row_idx, 0, QTableWidgetItem(inv.get("invoice_number", "")))
            self.table.setItem(row_idx, 1, QTableWidgetItem(inv.get("patient_name", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(inv.get("created_date", "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"Rs {inv.get('grand_total', 0.0):,.2f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(inv.get("payment_method", "")))
            
            # Align price item
            self.table.item(row_idx, 3).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
