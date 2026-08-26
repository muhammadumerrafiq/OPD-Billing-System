from models.bill import Bill
from models.patient import Patient
from models.doctor import Doctor
from models.procedure import Procedure
from models.lab_test import LabTest
from utils.pdf_generator import PDFGenerator
from utils.printer import PrinterManager
from utils.logger import logger

class BillingController:
    def __init__(self, view, parent_widget=None):
        self.view = view
        self.parent = parent_widget
        self.bind_signals()

    def bind_signals(self):
        self.view.patient_search_requested.connect(self.search_patient)
        self.view.save_bill_requested.connect(self.save_bill)
        self.view.print_invoice_requested.connect(self.print_invoice)

    def load_dropdown_data(self):
        """Loads all lists into billing selectors."""
        try:
            doctors = Doctor.get_active_doctors()
            procedures = Procedure.get_all_procedures()
            lab_tests = LabTest.get_all_lab_tests()

            self.view.load_doctors(doctors)
            self.view.load_procedures(procedures)
            self.view.load_lab_tests(lab_tests)
            logger.info("Dropdown active data loaded for Billing View.")
        except Exception as e:
            logger.error(f"Error loading dropdown data for billing: {str(e)}")

    def search_patient(self, search_query):
        """Searches patient and pushes details to view."""
        try:
            results = Patient.search_patients(search_query)
            if results:
                # Link first matched patient
                self.view.display_patient(results[0])
            else:
                self.view.display_patient(None)
        except Exception as e:
            logger.error(f"Error searching patient in billing: {str(e)}")
            self.view.display_patient(None)

    def save_bill(self, bill_data):
        """Saves bill transactions in database and generates standard PDF receipt."""
        try:
            invoice_num = Bill.create_bill(
                patient_id=bill_data['patient_id'],
                subtotal=bill_data['subtotal'],
                discount=bill_data['discount'],
                grand_total=bill_data['grand_total'],
                payment_method=bill_data['payment_method'],
                items=bill_data['items']
            )

            if invoice_num:
                # Retrieve fully populated bill dictionary (with items and patient info details)
                full_bill = Bill.get_bill_by_invoice(invoice_num)
                if full_bill:
                    # Generate standard PDF invoice inside Invoices/ subfolder
                    PDFGenerator.generate_invoice_pdf(full_bill)
                    
                    # Notify view
                    self.view.on_bill_saved_successfully(invoice_num)
                else:
                    raise Exception("Failed to retrieve saved bill details.")
            else:
                raise Exception("DB Manager returned None for invoice creation.")
        except Exception as e:
            logger.error(f"Failed to save bill transaction: {str(e)}")
            from views.widgets.toast import ToastNotification
            ToastNotification.show_error(f"Save failed: {str(e)}", self.parent)

    def print_invoice(self, invoice_number):
        """Retrieves bill details and opens Print Preview Dialog."""
        try:
            full_bill = Bill.get_bill_by_invoice(invoice_number)
            if full_bill:
                # Open native preview dialog
                PrinterManager.preview_invoice(full_bill, self.parent)
            else:
                raise Exception(f"Invoice {invoice_number} details not found.")
        except Exception as e:
            logger.error(f"Failed to print invoice {invoice_number}: {str(e)}")
            from views.widgets.toast import ToastNotification
            ToastNotification.show_error(f"Print failed: {str(e)}", self.parent)
