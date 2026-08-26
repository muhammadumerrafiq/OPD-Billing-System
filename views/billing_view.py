from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QFormLayout, QMessageBox, QCompleter
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon
from config import AppConfig
from views.widgets.toast import ToastNotification
from views.widgets.svg_icon import SVGIconFactory

class BillingView(QWidget):
    # Signals
    patient_search_requested = pyqtSignal(str)
    save_bill_requested = pyqtSignal(dict)
    print_invoice_requested = pyqtSignal(str) # Passes invoice number

    def __init__(self, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark_mode
        self.selected_patient = None
        self.bill_items = [] # Stores raw dict items: {category, item_name, quantity, price, total}
        self.active_doctors = []
        self.active_procedures = []
        self.active_lab_tests = []
        self.saved_invoice_number = None # Cache for print action after saving

        self.setup_ui()

    def setup_ui(self):
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # ----------------------------------------------------
        # LEFT COLUMN: Patient Lookup & Item Selection Form
        # ----------------------------------------------------
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)

        # Step 1: Patient Search Panel
        self.patient_search_panel = QFrame()
        self.patient_search_panel.setObjectName("ContentPanel")
        
        search_vbox = QVBoxLayout(self.patient_search_panel)
        search_vbox.setContentsMargins(15, 15, 15, 15)
        search_vbox.setSpacing(10)

        search_title = QLabel("Step 1: Locate Patient")
        search_title.setFont(QFont("Outfit", 11, QFont.Weight.Bold))
        search_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        search_vbox.addWidget(search_title)

        search_hbox = QHBoxLayout()
        search_hbox.setSpacing(8)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Patient ID, Name or Phone...")
        self.search_input.setMinimumHeight(36)
        self.search_input.returnPressed.connect(self.on_patient_search)
        search_hbox.addWidget(self.search_input, 1)

        self.search_btn = QPushButton("Search")
        self.search_btn.setObjectName("BtnOutline")
        self.search_btn.setMinimumHeight(36)
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn.clicked.connect(self.on_patient_search)
        search_hbox.addWidget(self.search_btn)
        search_vbox.addLayout(search_hbox)

        # Patient Info Display Card
        self.patient_info_card = QFrame()
        self.patient_info_card.setFrameShape(QFrame.Shape.StyledPanel)
        self.patient_info_card.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 108, 189, 0.05);
                border: 1px dashed #0F6CBD;
                border-radius: 8px;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        
        info_grid = QGridLayout(self.patient_info_card)
        info_grid.setContentsMargins(12, 12, 12, 12)
        info_grid.setSpacing(8)

        self.lbl_info_id = QLabel("<b>Patient ID:</b> -")
        self.lbl_info_name = QLabel("<b>Name:</b> -")
        self.lbl_info_age_gender = QLabel("<b>Age/Gender:</b> -")
        self.lbl_info_phone = QLabel("<b>Phone:</b> -")

        info_grid.addWidget(self.lbl_info_id, 0, 0)
        info_grid.addWidget(self.lbl_info_name, 0, 1)
        info_grid.addWidget(self.lbl_info_age_gender, 1, 0)
        info_grid.addWidget(self.lbl_info_phone, 1, 1)

        search_vbox.addWidget(self.patient_info_card)
        left_layout.addWidget(self.patient_search_panel)

        # Step 2: Add Items Panel
        self.items_panel = QFrame()
        self.items_panel.setObjectName("ContentPanel")
        
        items_vbox = QVBoxLayout(self.items_panel)
        items_vbox.setContentsMargins(15, 15, 15, 15)
        items_vbox.setSpacing(12)

        items_title = QLabel("Step 2: Add Services & Items")
        items_title.setFont(QFont("Outfit", 11, QFont.Weight.Bold))
        items_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        items_vbox.addWidget(items_title)

        # Tab views for categories (Clean layouts rather than long scrolled page)
        self.category_tabs = QWidget()
        tabs_layout = QFormLayout(self.category_tabs)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(8)

        # A. Doctor Consultation Section
        self.doctor_combo = QComboBox()
        self.doctor_combo.currentIndexChanged.connect(self.on_doctor_selected)
        btn_add_doc = QPushButton("Add")
        btn_add_doc.setObjectName("BtnOutline")
        btn_add_doc.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_doc.clicked.connect(self.add_doctor_item)
        
        doc_hbox = QHBoxLayout()
        doc_hbox.addWidget(self.doctor_combo, 1)
        doc_hbox.addWidget(btn_add_doc)
        tabs_layout.addRow(QLabel("Doctor Consultation"), doc_hbox)

        # B. Procedures Section
        self.proc_combo = QComboBox()
        self.proc_combo.setEditable(True)
        self.proc_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.proc_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.proc_combo.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.proc_combo.setPlaceholderText("Search or select procedure...")
        if self.proc_combo.lineEdit():
            self.proc_combo.lineEdit().setPlaceholderText("Search or select procedure...")
            self.proc_combo.lineEdit().returnPressed.connect(self.add_procedure_item)
        
        btn_add_proc = QPushButton("Add")
        btn_add_proc.setObjectName("BtnOutline")
        btn_add_proc.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_proc.clicked.connect(self.add_procedure_item)
        
        proc_hbox = QHBoxLayout()
        proc_hbox.addWidget(self.proc_combo, 1)
        proc_hbox.addWidget(btn_add_proc)
        tabs_layout.addRow(QLabel("Medical Procedure"), proc_hbox)

        # C. Lab Tests Section
        self.lab_combo = QComboBox()
        self.lab_combo.setEditable(True)
        self.lab_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.lab_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.lab_combo.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.lab_combo.setPlaceholderText("Search or select lab test...")
        if self.lab_combo.lineEdit():
            self.lab_combo.lineEdit().setPlaceholderText("Search or select lab test...")
            self.lab_combo.lineEdit().returnPressed.connect(self.add_lab_item)
        
        btn_add_lab = QPushButton("Add")
        btn_add_lab.setObjectName("BtnOutline")
        btn_add_lab.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_lab.clicked.connect(self.add_lab_item)
        
        lab_hbox = QHBoxLayout()
        lab_hbox.addWidget(self.lab_combo, 1)
        lab_hbox.addWidget(btn_add_lab)
        tabs_layout.addRow(QLabel("Lab Test"), lab_hbox)

        # D. Medicine Section (Manual details)
        self.med_name_input = QLineEdit()
        self.med_name_input.setPlaceholderText("Medicine Name")
        self.med_qty_spin = QSpinBox()
        self.med_qty_spin.setRange(1, 1000)
        self.med_qty_spin.setValue(1)
        self.med_price_spin = QDoubleSpinBox()
        self.med_price_spin.setRange(0, 10000)
        self.med_price_spin.setSingleStep(10)
        
        btn_add_med = QPushButton("Add Medicine")
        btn_add_med.setObjectName("BtnOutline")
        btn_add_med.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_med.clicked.connect(self.add_medicine_item)

        med_inputs_hbox = QHBoxLayout()
        med_inputs_hbox.addWidget(self.med_name_input, 2)
        med_inputs_hbox.addWidget(self.med_qty_spin, 1)
        med_inputs_hbox.addWidget(self.med_price_spin, 1)
        
        tabs_layout.addRow(QLabel("Prescribed Medicine"), med_inputs_hbox)
        tabs_layout.addRow("", btn_add_med)

        # E. Hospital Charges Section (Manual details)
        self.charge_desc_input = QLineEdit()
        self.charge_desc_input.setPlaceholderText("e.g. Disposable Syringe, Nebulizer Mask")
        self.charge_amount_spin = QDoubleSpinBox()
        self.charge_amount_spin.setRange(0, 50000)
        self.charge_amount_spin.setSingleStep(50)
        
        btn_add_charge = QPushButton("Add Charges")
        btn_add_charge.setObjectName("BtnOutline")
        btn_add_charge.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_charge.clicked.connect(self.add_charge_item)

        charge_hbox = QHBoxLayout()
        charge_hbox.addWidget(self.charge_desc_input, 2)
        charge_hbox.addWidget(self.charge_amount_spin, 1)
        
        tabs_layout.addRow(QLabel("Hospital Charges"), charge_hbox)
        tabs_layout.addRow("", btn_add_charge)

        items_vbox.addWidget(self.category_tabs)
        left_layout.addWidget(self.items_panel)

        main_layout.addLayout(left_layout, 5)

        # ----------------------------------------------------
        # RIGHT COLUMN: Bill Items Table & Totals Summary
        # ----------------------------------------------------
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)

        self.bill_container = QFrame()
        self.bill_container.setObjectName("ContentPanel")
        
        bill_vbox = QVBoxLayout(self.bill_container)
        bill_vbox.setContentsMargins(20, 20, 20, 20)
        bill_vbox.setSpacing(15)

        bill_title = QLabel("Patient Bill Items")
        bill_title.setFont(QFont("Outfit", 12, QFont.Weight.Bold))
        bill_title.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        bill_vbox.addWidget(bill_title)

        # Bill Items Grid Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Category", "Item Name", "Qty", "Unit Price", "Total", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(240)
        
        bill_vbox.addWidget(self.table, 1)

        # Summary Section (Live calculations)
        summary_panel = QFrame()
        summary_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(241, 245, 249, 0.5);
                border: 1px solid rgba(226, 232, 240, 0.8);
                border-radius: 8px;
            }
            QLabel {
                border: none;
                background: transparent;
            }}
        """)
        if self.is_dark:
            summary_panel.setStyleSheet("""
                QFrame {
                    background-color: rgba(30, 41, 59, 0.5);
                    border: 1px solid rgba(51, 65, 85, 0.8);
                    border-radius: 8px;
                }
                QLabel {
                    border: none;
                    background: transparent;
                }
            """)

        summary_layout = QGridLayout(summary_panel)
        summary_layout.setContentsMargins(15, 12, 15, 12)
        summary_layout.setSpacing(10)

        # Subtotal
        summary_layout.addWidget(QLabel("<b>Subtotal (Rs):</b>"), 0, 0)
        self.lbl_subtotal = QLabel("Rs 0.00")
        self.lbl_subtotal.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.lbl_subtotal.setAlignment(Qt.AlignmentFlag.AlignRight)
        summary_layout.addWidget(self.lbl_subtotal, 0, 1)

        # Discount type and value
        discount_label = QLabel("<b>Discount:</b>")
        summary_layout.addWidget(discount_label, 1, 0)
        
        disc_hbox = QHBoxLayout()
        disc_hbox.setSpacing(5)
        self.discount_type = QComboBox()
        self.discount_type.addItems(["Fixed Amount", "Percentage (%)"])
        self.discount_type.currentIndexChanged.connect(self.recalculate_totals)
        self.discount_val = QDoubleSpinBox()
        self.discount_val.setRange(0, 1000000)
        self.discount_val.setSingleStep(10)
        self.discount_val.valueChanged.connect(self.recalculate_totals)
        
        disc_hbox.addWidget(self.discount_type, 1)
        disc_hbox.addWidget(self.discount_val, 1)
        summary_layout.addLayout(disc_hbox, 1, 1)

        # Grand Total
        grand_lbl = QLabel("<b>Grand Total:</b>")
        grand_lbl.setFont(QFont("Outfit", 12, QFont.Weight.Bold))
        grand_lbl.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        summary_layout.addWidget(grand_lbl, 2, 0)

        self.lbl_grand_total = QLabel("Rs 0.00")
        self.lbl_grand_total.setFont(QFont("Outfit", 14, QFont.Weight.Bold))
        self.lbl_grand_total.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        self.lbl_grand_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        summary_layout.addWidget(self.lbl_grand_total, 2, 1)

        # Payment Methods
        summary_layout.addWidget(QLabel("<b>Payment Method:</b>"), 3, 0)
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cash", "Card", "Easypaisa", "JazzCash"])
        summary_layout.addWidget(self.payment_combo, 3, 1)

        bill_vbox.addWidget(summary_panel)

        # Primary Billing Action Buttons
        actions_hbox = QHBoxLayout()
        actions_hbox.setSpacing(10)

        self.save_bill_btn = QPushButton("Save Bill")
        self.save_bill_btn.setObjectName("BtnSuccess")
        self.save_bill_btn.setMinimumHeight(44)
        self.save_bill_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_bill_btn.clicked.connect(self.on_save_bill_clicked)
        actions_hbox.addWidget(self.save_bill_btn, 1)

        self.print_btn = QPushButton("Print Invoice")
        self.print_btn.setObjectName("BtnOutline")
        self.print_btn.setMinimumHeight(44)
        self.print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.print_btn.setEnabled(False) # Activated only after saving bill
        self.print_btn.clicked.connect(self.on_print_clicked)
        actions_hbox.addWidget(self.print_btn)

        self.clear_bill_btn = QPushButton("Clear/Reset")
        self.clear_bill_btn.setObjectName("BtnOutline")
        self.clear_bill_btn.setMinimumHeight(44)
        self.clear_bill_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_bill_btn.clicked.connect(self.reset_billing)
        actions_hbox.addWidget(self.clear_bill_btn)

        bill_vbox.addLayout(actions_hbox)
        right_layout.addWidget(self.bill_container)

        main_layout.addLayout(right_layout, 6)

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
        self.patient_search_panel.setStyleSheet(panel_style)
        self.items_panel.setStyleSheet(panel_style)
        self.bill_container.setStyleSheet(panel_style)

        # Active elements update colors
        # Clear print button outline if enabled/disabled
        self.lbl_grand_total.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY}; border: none;")

        # Update table actions icon color if icons exist
        self.update_action_icons()

    def set_theme(self, is_dark):
        self.is_dark = is_dark
        self.apply_theme_styling()

    def update_action_icons(self):
        pass # Handle item remove buttons dynamically

    # --- Patient Details Handling ---

    def on_patient_search(self):
        query = self.search_input.text().strip()
        if query:
            self.patient_search_requested.emit(query)

    def display_patient(self, patient_dict):
        """Displays patient details inside Step 1 card."""
        self.selected_patient = patient_dict
        if patient_dict:
            self.lbl_info_id.setText(f"<b>Patient ID:</b> {patient_dict['patient_id']}")
            self.lbl_info_name.setText(f"<b>Name:</b> {patient_dict['patient_name']}")
            self.lbl_info_age_gender.setText(f"<b>Age/Gender:</b> {patient_dict['age']} Yrs / {patient_dict['gender']}")
            self.lbl_info_phone.setText(f"<b>Phone:</b> {patient_dict['phone']}")
            ToastNotification.show_success("Patient linked successfully.", self)
        else:
            self.clear_patient_display()
            ToastNotification.show_error("No patient record found matching query.", self)

    def clear_patient_display(self):
        self.selected_patient = None
        self.lbl_info_id.setText("<b>Patient ID:</b> -")
        self.lbl_info_name.setText("<b>Name:</b> -")
        self.lbl_info_age_gender.setText("<b>Age/Gender:</b> -")
        self.lbl_info_phone.setText("<b>Phone:</b> -")

    # --- Data Load Methods ---

    def load_doctors(self, doctors_list):
        self.active_doctors = doctors_list
        self.doctor_combo.clear()
        self.doctor_combo.addItem("Select Doctor...", None)
        for doc in doctors_list:
            display = f"{doc['doctor_name']} ({doc['specialization']}) - Rs {doc['consultation_fee']:.0f}"
            self.doctor_combo.addItem(display, doc)

    def on_doctor_selected(self, index):
        # We can dynamically display fee in a label if we want, but combo displays it fine
        pass

    def load_procedures(self, procedures_list):
        self.active_procedures = procedures_list
        self.proc_combo.clear()
        self.proc_combo.addItem("Select Procedure...", None)
        for proc in procedures_list:
            display = f"[{proc['category']}] {proc['procedure_name']} - Rs {proc['procedure_fee']:.0f}"
            self.proc_combo.addItem(display, proc)

    def load_lab_tests(self, lab_tests_list):
        self.active_lab_tests = lab_tests_list
        self.lab_combo.clear()
        self.lab_combo.addItem("Select Lab Test...", None)
        for test in lab_tests_list:
            display = f"{test['test_name']} - Rs {test['test_fee']:.0f}"
            self.lab_combo.addItem(display, test)

    # --- Add Items to List Methods ---

    def add_bill_item(self, category, name, qty, price):
        """Adds a row item and updates totals."""
        total = qty * price
        
        # Check if item with same name & category already exists to merge it
        for item in self.bill_items:
            if item['category'] == category and item['item_name'] == name:
                item['quantity'] += qty
                item['total'] = item['quantity'] * item['price']
                self.populate_bill_table()
                self.recalculate_totals()
                return

        self.bill_items.append({
            "category": category,
            "item_name": name,
            "quantity": qty,
            "price": price,
            "total": total
        })
        self.populate_bill_table()
        self.recalculate_totals()

    def add_doctor_item(self):
        doc = self.doctor_combo.currentData()
        if doc:
            self.add_bill_item("Doctor Consultation", doc['doctor_name'], 1, doc['consultation_fee'])
            # Reset dropdown
            self.doctor_combo.setCurrentIndex(0)
        else:
            ToastNotification.show_error("Please select a valid doctor.", self)

    def add_procedure_item(self):
        proc = self.proc_combo.currentData()
        if not proc:
            typed_text = self.proc_combo.currentText().strip().lower()
            if typed_text:
                # 1. Exact match on name or display format
                for p in self.active_procedures:
                    display_str = f"[{p['category']}] {p['procedure_name']} - Rs {p['procedure_fee']:.0f}"
                    if typed_text == display_str.lower() or typed_text == p['procedure_name'].lower():
                        proc = p
                        break
                # 2. Prefix match
                if not proc:
                    for p in self.active_procedures:
                        if p['procedure_name'].lower().startswith(typed_text):
                            proc = p
                            break
                # 3. Substring match
                if not proc:
                    for p in self.active_procedures:
                        if typed_text in p['procedure_name'].lower():
                            proc = p
                            break
        if proc:
            self.add_bill_item("Procedure", proc['procedure_name'], 1, proc['procedure_fee'])
            self.proc_combo.setCurrentIndex(0)
            self.proc_combo.setEditText("")
        else:
            ToastNotification.show_error("Please select a valid procedure.", self)

    def add_lab_item(self):
        test = self.lab_combo.currentData()
        if not test:
            typed_text = self.lab_combo.currentText().strip().lower()
            if typed_text:
                # 1. Exact match on name or display format
                for t in self.active_lab_tests:
                    display_str = f"{t['test_name']} - Rs {t['test_fee']:.0f}"
                    if typed_text == display_str.lower() or typed_text == t['test_name'].lower():
                        test = t
                        break
                # 2. Prefix match
                if not test:
                    for t in self.active_lab_tests:
                        if t['test_name'].lower().startswith(typed_text):
                            test = t
                            break
                # 3. Substring match
                if not test:
                    for t in self.active_lab_tests:
                        if typed_text in t['test_name'].lower():
                            test = t
                            break
        if test:
            self.add_bill_item("Lab Test", test['test_name'], 1, test['test_fee'])
            self.lab_combo.setCurrentIndex(0)
            self.lab_combo.setEditText("")
        else:
            ToastNotification.show_error("Please select a valid laboratory test.", self)

    def add_medicine_item(self):
        med_name = self.med_name_input.text().strip()
        qty = self.med_qty_spin.value()
        price = self.med_price_spin.value()

        if not med_name:
            ToastNotification.show_error("Medicine name is required.", self)
            self.med_name_input.setFocus()
            return
        if price <= 0:
            ToastNotification.show_error("Price must be greater than 0.", self)
            self.med_price_spin.setFocus()
            return

        self.add_bill_item("Medicine", med_name, qty, price)
        
        # Reset fields
        self.med_name_input.clear()
        self.med_qty_spin.setValue(1)
        self.med_price_spin.setValue(0.0)

    def add_charge_item(self):
        desc = self.charge_desc_input.text().strip()
        amount = self.charge_amount_spin.value()

        if not desc:
            ToastNotification.show_error("Description is required.", self)
            self.charge_desc_input.setFocus()
            return
        if amount <= 0:
            ToastNotification.show_error("Amount must be greater than 0.", self)
            self.charge_amount_spin.setFocus()
            return

        self.add_bill_item("Hospital Charges", desc, 1, amount)

        # Reset fields
        self.charge_desc_input.clear()
        self.charge_amount_spin.setValue(0.0)

    # --- Table Operations ---

    def populate_bill_table(self):
        self.table.setRowCount(0)
        self.table.setRowCount(len(self.bill_items))
        
        for row_idx, item in enumerate(self.bill_items):
            self.table.setItem(row_idx, 0, QTableWidgetItem(item['category']))
            self.table.setItem(row_idx, 1, QTableWidgetItem(item['item_name']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(item['quantity'])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"Rs {item['price']:,.2f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"Rs {item['total']:,.2f}"))
            
            # Align number cells
            self.table.item(row_idx, 2).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.item(row_idx, 3).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.item(row_idx, 4).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            # Remove Button
            remove_btn = QPushButton()
            remove_btn.setFixedSize(30, 26)
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(239, 68, 68, 0.1);
                    border-radius: 4px;
                }
            """)
            del_pix = SVGIconFactory.get_icon("delete", color=AppConfig.COLOR_DANGER, size=(16, 16))
            remove_btn.setIcon(del_pix)
            remove_btn.clicked.connect(lambda checked, idx=row_idx: self.remove_bill_item(idx))
            
            # Put in cell
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_layout.addWidget(remove_btn)
            self.table.setCellWidget(row_idx, 5, cell_widget)

    def remove_bill_item(self, index):
        if 0 <= index < len(self.bill_items):
            self.bill_items.pop(index)
            self.populate_bill_table()
            self.recalculate_totals()

    # --- Calculations ---

    def recalculate_totals(self):
        subtotal = sum(item['total'] for item in self.bill_items)
        self.lbl_subtotal.setText(f"Rs {subtotal:,.2f}")

        # Compute discount
        discount_val = self.discount_val.value()
        if self.discount_type.currentIndex() == 1: # Percentage
            if discount_val > 100:
                discount_val = 100
                self.discount_val.setValue(100)
            discount_amount = (discount_val / 100.0) * subtotal
        else: # Fixed
            if discount_val > subtotal:
                discount_val = subtotal
                self.discount_val.setValue(subtotal)
            discount_amount = discount_val

        grand_total = subtotal - discount_amount
        self.lbl_grand_total.setText(f"Rs {grand_total:,.2f}")

    # --- Save & Print ---

    def on_save_bill_clicked(self):
        if not self.selected_patient:
            ToastNotification.show_error("Please select a patient first.", self)
            self.search_input.setFocus()
            return
        if not self.bill_items:
            ToastNotification.show_error("Please add at least one bill item.", self)
            return

        # Calculate values
        subtotal = sum(item['total'] for item in self.bill_items)
        discount_val = self.discount_val.value()
        
        if self.discount_type.currentIndex() == 1: # %
            discount_amount = (discount_val / 100.0) * subtotal
        else: # Fixed
            discount_amount = discount_val
            
        grand_total = subtotal - discount_amount

        bill_data = {
            "patient_id": self.selected_patient['patient_id'],
            "subtotal": subtotal,
            "discount": discount_amount,
            "grand_total": grand_total,
            "payment_method": self.payment_combo.currentText(),
            "items": self.bill_items
        }

        self.save_bill_requested.emit(bill_data)

    def on_bill_saved_successfully(self, invoice_number):
        """Called by controller after bill is stored in database."""
        self.saved_invoice_number = invoice_number
        self.print_btn.setEnabled(True)
        ToastNotification.show_success(f"Bill saved as {invoice_number}.", self)
        
        # Open confirmation to print immediately
        reply = QMessageBox.question(
            self,
            "Bill Saved",
            f"Bill {invoice_number} saved successfully.\nWould you like to print/preview the invoice now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.on_print_clicked()

    def on_print_clicked(self):
        if self.saved_invoice_number:
            self.print_invoice_requested.emit(self.saved_invoice_number)
        else:
            ToastNotification.show_error("Please save the bill before printing.", self)

    def reset_billing(self):
        self.clear_patient_display()
        self.search_input.clear()
        self.bill_items.clear()
        self.populate_bill_table()
        self.discount_val.setValue(0.0)
        self.discount_type.setCurrentIndex(0)
        self.payment_combo.setCurrentIndex(0)
        self.recalculate_totals()
        self.print_btn.setEnabled(False)
        self.saved_invoice_number = None
        self.search_input.setFocus()
