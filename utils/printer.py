import os
import shutil
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from database.db_manager import DatabaseManager
from utils.logger import logger

class PrinterManager:
    @staticmethod
    def get_hospital_settings():
        """Loads hospital details from database."""
        db = DatabaseManager()
        settings = {}
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings;")
                settings = {row[0]: row[1] for row in cursor.fetchall()}
        except Exception as e:
            logger.error(f"Failed to fetch settings for print HTML: {str(e)}")
        return settings

    @staticmethod
    def generate_invoice_html(bill_data):
        """Generates a print-friendly HTML document matching the PDF receipt.
        This uses basic HTML/CSS table elements compatible with QTextDocument.
        """
        settings = PrinterManager.get_hospital_settings()
        hospital_name = settings.get("hospital_name", "Bismel Medical Center")
        hospital_address = settings.get("hospital_address", "Sector G-11 Markaz, Islamabad, Pakistan")
        hospital_phone = settings.get("hospital_phone", "+92-51-1234567")
        hospital_email = settings.get("hospital_email", "info@bismelmedical.com")
        # invoice_footer = settings.get("invoice_footer", "Thank You For Visiting Bismel Medical Center")

        # Check for logo
        import sys
        if getattr(sys, 'frozen', False):
            logo_path = os.path.join(sys._MEIPASS, "logo.jpeg")
        else:
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logo_path = os.path.join(project_dir, "logo.jpeg")
        if os.path.exists(logo_path):
            logo_url = logo_path.replace(os.sep, "/")
            logo_html = f'<img src="file:///{logo_url}" width="80" height="80" style="border-radius:4px;">'
        else:
            logo_html = ''

        # HTML Structure
        html = f"""
        <html>
        <head>
        <style>
            body {{
                font-family: 'Helvetica', 'Arial', sans-serif;
                color: #1E293B;
                margin: 15pt;
            }}
            .header-table {{
                width: 100%;
                margin-bottom: 15pt;
            }}
            .hospital-title {{
                font-size: 18pt;
                font-weight: bold;
                color: #0F6CBD;
            }}
            .invoice-title {{
                font-size: 16pt;
                font-weight: bold;
                color: #0F6CBD;
                text-align: right;
            }}
            .header-subtext {{
                font-size: 10pt;
                color: #475569;
                line-height: 1.4;
            }}
            .meta-text {{
                font-size: 10pt;
                color: #475569;
                text-align: right;
                line-height: 1.4;
            }}
            .patient-box {{
                width: 100%;
                background-color: #F8FAFC;
                border: 1pt solid #E2E8F0;
                border-collapse: collapse;
                margin-bottom: 15pt;
            }}
            .patient-box td {{
                padding: 6pt 10pt;
                font-size: 11pt;
                border: none;
            }}
            .items-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 15pt;
            }}
            .items-table th {{
                background-color: #0F6CBD;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 11pt;
                padding: 8pt 6pt;
                border: 1pt solid #E2E8F0;
                text-align: left;
            }}
            .items-table td {{
                padding: 8pt 6pt;
                font-size: 11pt;
                border: 1pt solid #E2E8F0;
            }}
            .items-table tr.even-row td {{
                background-color: #F8FAFC;
            }}
            .summary-table {{
                width: 100%;
                margin-bottom: 30pt;
            }}
            .summary-label {{
                font-weight: bold;
                font-size: 11pt;
                text-align: right;
                padding: 4pt;
            }}
            .summary-value {{
                font-weight: bold;
                font-size: 12pt;
                text-align: right;
                color: #0F6CBD;
                padding: 4pt;
                width: 140pt;
            }}
            .footer-text {{
                text-align: center;
                font-style: italic;
                font-size: 11pt;
                color: #0F6CBD;
                margin-top: 20pt;
            }}
        </style>
        </head>
        <body>
            <!-- Header Table -->
            <table class="header-table" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                    <td valign="middle" align="left" style="border:none;">
                        <table cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td valign="middle" style="padding-right:15px; border:none;">
                                    {logo_html}
                                </td>
                                <td valign="middle" style="border:none; text-align:left;">
                                    <div class="hospital-title">{hospital_name}</div>
                                    <div class="header-subtext">{hospital_address}<br>Phone: {hospital_phone}<br>Email: {hospital_email}</div>
                                </td>
                            </tr>
                        </table>
                    </td>
                    <td valign="middle" align="right" style="border:none; text-align:right;">
                        <div class="invoice-title">OPD INVOICE</div>
                        <div class="meta-text">
                            <b>Invoice #:</b> {bill_data['invoice_number']}<br>
                            <b>Date:</b> {bill_data['created_date']}<br>
                            <b>Payment:</b> {bill_data['payment_method']}
                        </div>
                    </td>
                </tr>
            </table>

            <hr style="border: 0; border-top: 2px solid #0F6CBD; margin-bottom: 10px;">

            <!-- Patient Info Box -->
            <table class="patient-box" cellpadding="0" cellspacing="0">
                <tr>
                    <td><b>Patient ID:</b> {bill_data['patient_id']}</td>
                    <td><b>Patient Name:</b> {bill_data['patient_name']}</td>
                </tr>
                <tr>
                    <td><b>Age / Gender:</b> {bill_data['age']} Yrs / {bill_data['gender']}</td>
                    <td><b>Phone:</b> {bill_data['phone']}</td>
                </tr>
            </table>

            <!-- Bill Items Table -->
            <table class="items-table">
                <thead>
                    <tr>
                        <th width="25%">Category</th>
                        <th width="40%">Service Description</th>
                        <th width="10%">Qty</th>
                        <th width="12%">Price</th>
                        <th width="13%">Total</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx, item in enumerate(bill_data['items']):
            row_class = "even-row" if idx % 2 == 1 else ""
            html += f"""
                    <tr class="{row_class}">
                        <td>{item['category']}</td>
                        <td>{item['item_name']}</td>
                        <td>{item['quantity']}</td>
                        <td>{item['price']:.2f}</td>
                        <td>{item['total']:.2f}</td>
                    </tr>
            """

        html += f"""
                </tbody>
            </table>

            <!-- Summary Table -->
            <table class="summary-table" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="border:none;"></td>
                    <td class="summary-label" style="border:none;">Subtotal:</td>
                    <td class="summary-value" style="border:none; border-bottom:1px solid #E2E8F0;">Rs {bill_data['subtotal']:.2f}</td>
                </tr>
                <tr>
                    <td style="border:none;"></td>
                    <td class="summary-label" style="border:none;">Discount:</td>
                    <td class="summary-value" style="border:none; border-bottom:1px solid #E2E8F0;">Rs {bill_data['discount']:.2f}</td>
                </tr>
                <tr>
                    <td style="border:none;"></td>
                    <td class="summary-label" style="border:none;">Grand Total:</td>
                    <td class="summary-value" style="border:none; border-bottom:2px solid #0F6CBD; font-size:12px; font-weight:bold;">Rs {bill_data['grand_total']:.2f}</td>
                </tr>
            </table>

        </body>
        </html>
        """
        return html

    @classmethod
    def print_invoice(cls, bill_data, parent_window=None):
        """Triggers the PyQt print dialog and prints the invoice."""
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintDialog(printer, parent_window)
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                doc = QTextDocument()
                html_content = cls.generate_invoice_html(bill_data)
                doc.setHtml(html_content)
                doc.print(printer)
                logger.info(f"Invoice {bill_data['invoice_number']} printed successfully.")
                return True
        except Exception as e:
            logger.error(f"Printing failed: {str(e)}")
            if parent_window:
                QMessageBox.critical(parent_window, "Print Error", f"Failed to print invoice: {str(e)}")
        return False

    @classmethod
    def preview_invoice(cls, bill_data, parent_window=None):
        """Opens a native PyQt6 Print Preview dialog for the invoice."""
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            preview = QPrintPreviewDialog(printer, parent_window)
            
            doc = QTextDocument()
            html_content = cls.generate_invoice_html(bill_data)
            doc.setHtml(html_content)

            def handle_paint(preview_printer):
                doc.print(preview_printer)

            preview.paintRequested.connect(handle_paint)
            preview.exec()
            return True
        except Exception as e:
            logger.error(f"Print preview failed: {str(e)}")
            if parent_window:
                QMessageBox.critical(parent_window, "Preview Error", f"Failed to show print preview: {str(e)}")
        return False

    @classmethod
    def export_invoice_pdf(cls, bill_data, parent_window=None):
        """Allows exporting the invoice to a custom PDF file path selected by the user."""
        try:
            # Let ReportLab generate the PDF first in /Invoices/
            from utils.pdf_generator import PDFGenerator
            generated_path = PDFGenerator.generate_invoice_pdf(bill_data)

            if not generated_path or not os.path.exists(generated_path):
                raise FileNotFoundError("ReportLab failed to generate standard invoice PDF.")

            # Prompt user for export path
            default_name = f"{bill_data['invoice_number']}.pdf"
            export_path, _ = QFileDialog.getSaveFileName(
                parent_window,
                "Export Invoice PDF",
                default_name,
                "PDF Files (*.pdf)"
            )

            if export_path:
                shutil.copy(generated_path, export_path)
                logger.info(f"Exported invoice PDF to: {export_path}")
                return True
        except Exception as e:
            logger.error(f"PDF Export failed: {str(e)}")
            if parent_window:
                QMessageBox.critical(parent_window, "Export Error", f"Failed to export PDF: {str(e)}")
        return False

    @staticmethod
    def generate_patient_slip_html(patient_data, doctor_data=None):
        """Generates a print-friendly HTML document for a patient registration / visiting slip."""
        settings = PrinterManager.get_hospital_settings()
        hospital_name = settings.get("hospital_name", "Bismel Medical Center")

        import sys
        if getattr(sys, 'frozen', False):
            logo_path = os.path.join(sys._MEIPASS, "logo.jpeg")
        else:
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logo_path = os.path.join(project_dir, "logo.jpeg")
        if os.path.exists(logo_path):
            logo_url = logo_path.replace(os.sep, "/")
            # Moderately enlarged logo to visually balance header
            logo_html = f'<img src="file:///{logo_url}" width="92" height="92">'
        else:
            logo_html = ''

        if doctor_data:
            doctor_display = f"{doctor_data.get('doctor_name', 'N/A')} ({doctor_data.get('specialization', 'N/A')})"
        else:
            doctor_display = "N/A (General / OPD)"

        cnic_display = ''

        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Shorter underline for writing lines: 14 spaces
        uline = "<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>"

        # Space filler pushing footer cleanly to the bottom of the page
        rx_blank_lines = "&nbsp;"

        html = f"""
        <html>
        <head>
        <style>
            body {{
                font-family: 'Helvetica', 'Arial', sans-serif;
                color: #1E293B;
                margin: 0pt 24pt 0pt 24pt;
            }}
            .hospital-title {{
                font-size: 22pt;
                font-weight: bold;
                color: #0F6CBD;
                text-align: center;
                letter-spacing: 0.5px;
            }}
            .slip-title {{
                font-size: 13.5pt;
                font-weight: bold;
                color: #0F6CBD;
                text-align: center;
                letter-spacing: 1.2px;
            }}
            .consent-text {{
                text-align: center;
                font-size: 10pt;
                color: #475569;
                font-style: italic;
            }}
            .patient-table td {{
                font-size: 11pt;
                border: none;
                line-height: 1.35;
            }}
            .rx-title {{
                font-size: 26pt;
                font-weight: bold;
                font-style: italic;
                color: #1E293B;
                line-height: 1;
            }}
            .rx-free-space {{
                width: 100%;
                font-size: 280pt;
                line-height: 280pt;
                color: transparent;
            }}
            .footer-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 9.5pt;
                color: #475569;
                line-height: 1.55;
            }}
            .footer-table td {{
                border: none;
            }}
        </style>
        </head>
        <body>
            <!-- Header Table: Logo (20%), Centered Titles (60%), Spacer (20%) -->
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td valign="top" align="left" width="20%" style="border:none;">
                        {logo_html}
                    </td>
                    <td valign="top" align="center" width="60%" style="border:none; text-align:center; padding-top:2pt;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td align="center" class="hospital-title">{hospital_name}</td>
                            </tr>
                            <tr>
                                <td height="5" style="font-size:5pt; line-height:5pt;">&nbsp;</td>
                            </tr>
                            <tr>
                                <td align="center" class="slip-title">PATIENT REGISTRATION SLIP</td>
                            </tr>
                        </table>
                    </td>
                    <td valign="top" width="20%" style="border:none;">
                        &nbsp;
                    </td>
                </tr>
            </table>

            <!-- Visible breathing room between PATIENT REGISTRATION SLIP and Consulting Doctor / Date -->
            <div style="font-size: 12pt; line-height: 12pt;">&nbsp;</div>

            <!-- Consulting Doctor & Date -->
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td width="20%" style="border:none;">&nbsp;</td>
                    <td align="left" width="52%" style="border:none; font-size:12.5pt; color:#1E293B;">
                        <b>Consulting Doctor:</b> <span style="color:#0F6CBD; font-weight:bold;">{doctor_display}</span>
                    </td>
                    <td align="right" width="28%" style="border:none; text-align:right; font-size:11pt; color:#1E293B;">
                        <b>Date:</b> {current_date}
                    </td>
                </tr>
            </table>

            <!-- Visible breathing room between Consulting Doctor / Date and Consent statement -->
            <div style="font-size: 10pt; line-height: 10pt;">&nbsp;</div>

            <!-- Consent Statement Centered -->
            <div class="consent-text">I hereby give permission for my checkup.</div>

            <!-- Visible breathing room between Consent statement and Patient Information -->
            <div style="font-size: 6pt; line-height: 6pt;">&nbsp;</div>
            <hr style="border: 0; border-top: 1.5px solid #0F6CBD; margin: 0 0 6pt 0;">

            <!-- Two-Column Patient Information -->
            <table class="patient-table" width="100%" cellpadding="4" cellspacing="0" border="0">
                <tr>
                    <td width="50%"><b>Patient ID:</b> {patient_data.get('patient_id') or 'New Patient'}</td>
                    <td width="50%"><b>Patient Name:</b> {patient_data.get('patient_name', '')}</td>
                </tr>
                <tr>
                    <td><b>Age / Gender:</b> {patient_data.get('age', '')} Yrs / {patient_data.get('gender', '')}</td>
                    <td><b>Phone:</b> {patient_data.get('phone', '')}</td>
                </tr>
            </table>

            <hr style="border: 0; border-top: 1px solid #CBD5E1; margin: 6pt 0 8pt 0;">

            <!-- Upper Vitals & Rx Header: Divider stops at BSR level -->
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <!-- Left: 6 Vertical Vitals with moderate vertical line spacing -->
                    <td width="28%" valign="top" style="border:none; padding-right:12pt;">
                        <table cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td style="font-size:11pt; font-weight:bold; color:#1E293B; width:31pt; padding:9pt 0; white-space:nowrap; border:none;">B.P</td>
                                <td style="font-size:11pt; color:#475569; padding:9pt 0 9pt 2pt; white-space:nowrap; border:none;">{uline}</td>
                            </tr>
                            <tr>
                                <td style="font-size:11pt; font-weight:bold; color:#1E293B; width:31pt; padding:9pt 0; white-space:nowrap; border:none;">Temp</td>
                                <td style="font-size:11pt; color:#475569; padding:9pt 0 9pt 2pt; white-space:nowrap; border:none;">{uline}</td>
                            </tr>
                            <tr>
                                <td style="font-size:11pt; font-weight:bold; color:#1E293B; width:31pt; padding:9pt 0; white-space:nowrap; border:none;">SPO 2</td>
                                <td style="font-size:11pt; color:#475569; padding:9pt 0 9pt 2pt; white-space:nowrap; border:none;">{uline}</td>
                            </tr>
                            <tr>
                                <td style="font-size:11pt; font-weight:bold; color:#1E293B; width:31pt; padding:9pt 0; white-space:nowrap; border:none;">P.R</td>
                                <td style="font-size:11pt; color:#475569; padding:9pt 0 9pt 2pt; white-space:nowrap; border:none;">{uline}</td>
                            </tr>
                            <tr>
                                <td style="font-size:11pt; font-weight:bold; color:#1E293B; width:31pt; padding:9pt 0; white-space:nowrap; border:none;">Weight</td>
                                <td style="font-size:11pt; color:#475569; padding:9pt 0 9pt 2pt; white-space:nowrap; border:none;">{uline}</td>
                            </tr>
                            <tr>
                                <td style="font-size:11pt; font-weight:bold; color:#1E293B; width:31pt; padding:9pt 0; white-space:nowrap; border:none;">BSR</td>
                                <td style="font-size:11pt; color:#475569; padding:9pt 0 9pt 2pt; white-space:nowrap; border:none;">{uline}</td>
                            </tr>
                        </table>
                    </td>

                    <!-- Vertical Divider extending down to BSR level -->
                    <td width="1" style="border:none; border-left:1.5px solid #94A3B8; padding:0;" valign="top"><div style="color:transparent; font-size:1pt; line-height:1;">&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;</div></td>

                    <!-- Rx Area -->
                    <td width="72%" valign="top" style="border:none; padding-left:16pt; padding-top:0;">
                        <div class="rx-title">Rx</div>
                    </td>
                </tr>
            </table>

            <!-- Blank Rx Space pushing Court / Footer down toward the bottom -->
            <div class="rx-free-space">
                {rx_blank_lines}
            </div>

            <!-- Not Valid for Court Section positioned near bottom -->
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td width="36%" style="border-bottom: 1px solid #CBD5E1; height: 10pt;">&nbsp;</td>
                    <td width="28%" style="text-align:center; font-size:9.5pt; font-weight:bold; color:#64748B; white-space:nowrap; padding:0 6pt;">
                        Not Valid for Court
                    </td>
                    <td width="36%" style="border-bottom: 1px solid #CBD5E1; height: 10pt;">&nbsp;</td>
                </tr>
            </table>

            <hr style="border: 0; border-top: 1.5px solid #0F6CBD; margin-top: 6pt; margin-bottom: 6pt;">

            <!-- Footer -->
            <table class="footer-table" width="100%" cellpadding="2" cellspacing="0" border="0">
                <tr>
                    <td align="left" width="55%">
                        <b>Address:</b> The One Mall New City Phase 2 Wah Cantt
                    </td>
                    <td align="right" width="45%" style="text-align:right;">
                        <b>Mail:</b> bismelmedicalcenter8@gmail.com
                    </td>
                </tr>
                <tr>
                    <td align="left" width="55%">
                        <b>Phone:</b> 0310-1111935, 0303-0151111
                    </td>
                    <td align="right" width="45%" style="text-align:right;">
                        <b>Website:</b> https://bismelmedicalcenter.com/
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        return html

    @classmethod
    def preview_patient_slip(cls, patient_data, doctor_data=None, parent_window=None):
        """Opens a native PyQt6 Print Preview dialog for the patient registration slip."""
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            preview = QPrintPreviewDialog(printer, parent_window)
            
            doc = QTextDocument()
            html_content = cls.generate_patient_slip_html(patient_data, doctor_data)
            doc.setHtml(html_content)

            def handle_paint(preview_printer):
                doc.print(preview_printer)

            preview.paintRequested.connect(handle_paint)
            preview.exec()
            return True
        except Exception as e:
            logger.error(f"Patient slip preview failed: {str(e)}")
            if parent_window:
                QMessageBox.critical(parent_window, "Preview Error", f"Failed to show print preview: {str(e)}")
        return False
