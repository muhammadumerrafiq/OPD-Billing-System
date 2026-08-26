import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from database.db_manager import DatabaseManager
from utils.logger import logger

class PDFGenerator:
    @staticmethod
    def generate_invoice_pdf(bill_data):
        """Generates a professional hospital invoice PDF.
        bill_data must include: invoice_number, patient_id, patient_name, father_name, age, gender, phone,
        subtotal, discount, grand_total, payment_method, created_date, and items list.
        """
        db = DatabaseManager()
        # Retrieve hospital information from settings
        settings = {}
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings;")
                settings = {row[0]: row[1] for row in cursor.fetchall()}
        except Exception as e:
            logger.error(f"Failed to fetch settings for PDF: {str(e)}")

        hospital_name = settings.get("hospital_name", "Bismel Medical Center")
        hospital_address = settings.get("hospital_address", "Sector G-11 Markaz, Islamabad, Pakistan")
        hospital_phone = settings.get("hospital_phone", "+92-51-1234567")
        hospital_email = settings.get("hospital_email", "info@bismelmedical.com")

        # Set up output directory
        import sys
        if getattr(sys, 'frozen', False):
            project_dir = os.path.dirname(sys.executable)
        else:
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        invoices_dir = os.path.join(project_dir, "Invoices")
        os.makedirs(invoices_dir, exist_ok=True)

        pdf_filename = f"{bill_data['invoice_number']}.pdf"
        pdf_path = os.path.join(invoices_dir, pdf_filename)

        try:
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=letter,
                rightMargin=36,
                leftMargin=36,
                topMargin=36,
                bottomMargin=36
            )

            story = []
            styles = getSampleStyleSheet()

            # Define Custom Color Palette (Hospital Theme)
            primary_color = colors.HexColor("#0F6CBD")   # Dark Blue
            secondary_color = colors.HexColor("#38BDF8") # Sky Blue
            dark_text_color = colors.HexColor("#1E293B")  # Charcoal
            light_bg_color = colors.HexColor("#F8FAFC")   # Light slate
            line_color = colors.HexColor("#E2E8F0")

            # Custom styles
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=22,
                leading=26,
                textColor=primary_color
            )
            hospital_contact_style = ParagraphStyle(
                'HospitalContact',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=10.5,
                leading=14,
                textColor=dark_text_color
            )
            invoice_title_style = ParagraphStyle(
                'InvoiceTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=16,
                leading=19,
                textColor=primary_color,
                alignment=2 # Right aligned
            )
            invoice_meta_style = ParagraphStyle(
                'InvoiceMeta',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=10.5,
                leading=14,
                textColor=dark_text_color,
                alignment=2 # Right aligned
            )
            section_heading_style = ParagraphStyle(
                'SectionHeading',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=13,
                leading=16,
                textColor=primary_color
            )
            patient_info_style = ParagraphStyle(
                'PatientInfo',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=11,
                leading=15,
                textColor=dark_text_color
            )
            table_header_style = ParagraphStyle(
                'TableHeader',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=11,
                leading=13,
                textColor=colors.white
            )
            table_cell_style = ParagraphStyle(
                'TableCell',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=10.5,
                leading=14,
                textColor=dark_text_color
            )
            summary_label_style = ParagraphStyle(
                'SummaryLabel',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=11.5,
                leading=14,
                textColor=dark_text_color,
                alignment=2
            )
            summary_value_style = ParagraphStyle(
                'SummaryValue',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=12,
                leading=14,
                textColor=primary_color,
                alignment=2
            )
            footer_style = ParagraphStyle(
                'FooterText',
                parent=styles['Normal'],
                fontName='Helvetica-Oblique',
                fontSize=10,
                leading=14,
                textColor=primary_color,
                alignment=1 # Centered
            )

            # --- Header Layout ---
            logo_img = None
            if getattr(sys, 'frozen', False):
                logo_path = os.path.join(sys._MEIPASS, "logo.jpeg")
            else:
                logo_path = os.path.join(project_dir, "logo.jpeg")
            if os.path.exists(logo_path):
                try:
                    logo_img = Image(logo_path, width=1.1 * inch, height=1.1 * inch)
                except Exception as e:
                    logger.error(f"Failed to load logo.jpeg for PDF: {str(e)}")

            if logo_img:
                header_data = [
                    [
                        logo_img,
                        Paragraph(f"<b><font size=\"13\" color=\"#1E293B\">{hospital_name}</font></b><br/><font size=\"10.5\" color=\"#475569\">{hospital_address}<br/>Phone: {hospital_phone}<br/>Email: {hospital_email}</font>", hospital_contact_style),
                        Paragraph("<b><font size=\"14\" color=\"#0F6CBD\">OPD INVOICE</font></b><br/>" + f"<font size=\"11\" color=\"#1E293B\"><b>Invoice #:</b> {bill_data['invoice_number']}<br/><b>Date:</b> {bill_data['created_date']}<br/><b>Payment:</b> {bill_data['payment_method']}</font>", invoice_meta_style)
                    ]
                ]
                header_table = Table(header_data, colWidths=[1.3 * inch, 3.1 * inch, 3.1 * inch])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                ]))
            else:
                header_data = [
                    [
                        Paragraph(f"<b>{hospital_name}</b>", title_style),
                        Paragraph("<b>OPD INVOICE</b>", invoice_title_style)
                    ],
                    [
                        Paragraph(f"{hospital_address}<br/>Phone: {hospital_phone}<br/>Email: {hospital_email}", hospital_contact_style),
                        Paragraph(f"<b>Invoice #:</b> {bill_data['invoice_number']}<br/><b>Date:</b> {bill_data['created_date']}<br/><b>Payment:</b> {bill_data['payment_method']}", invoice_meta_style)
                    ]
                ]
                header_table = Table(header_data, colWidths=[4.0 * inch, 3.5 * inch])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                ]))
            story.append(header_table)
            story.append(Spacer(1, 15))

            # Horizontal line separator
            sep_table = Table([[""]], colWidths=[7.5 * inch])
            sep_table.setStyle(TableStyle([
                ('LINEBELOW', (0,0), (-1,-1), 1.5, primary_color),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 2),
            ]))
            story.append(sep_table)
            story.append(Spacer(1, 12))

            # --- Patient Details Section ---
            pat_data = [
                [
                    Paragraph(f"<b>Patient ID:</b> {bill_data['patient_id']}", patient_info_style),
                    Paragraph(f"<b>Patient Name:</b> {bill_data['patient_name']}", patient_info_style)
                ],
                [
                    Paragraph(f"<b>Age / Gender:</b> {bill_data['age']} Yrs / {bill_data['gender']}", patient_info_style),
                    Paragraph(f"<b>Phone:</b> {bill_data['phone']}", patient_info_style)
                ]
            ]
            pat_table = Table(pat_data, colWidths=[3.75 * inch, 3.75 * inch])
            pat_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BACKGROUND', (0,0), (-1,-1), light_bg_color),
                ('BOX', (0,0), (-1,-1), 0.5, line_color),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(Paragraph("<b>PATIENT DETAILS</b>", section_heading_style))
            story.append(Spacer(1, 5))
            story.append(pat_table)
            story.append(Spacer(1, 15))

            # --- Invoice Items Table ---
            item_headers = [
                Paragraph("<b>Category</b>", table_header_style),
                Paragraph("<b>Service Description</b>", table_header_style),
                Paragraph("<b>Qty</b>", table_header_style),
                Paragraph("<b>Price (Rs)</b>", table_header_style),
                Paragraph("<b>Total (Rs)</b>", table_header_style)
            ]
            item_data = [item_headers]

            for item in bill_data['items']:
                item_data.append([
                    Paragraph(item['category'], table_cell_style),
                    Paragraph(item['item_name'], table_cell_style),
                    Paragraph(str(item['quantity']), table_cell_style),
                    Paragraph(f"{item['price']:.2f}", table_cell_style),
                    Paragraph(f"{item['total']:.2f}", table_cell_style)
                ])

            # Column widths summing to 7.5 inches
            items_table = Table(item_data, colWidths=[1.8 * inch, 2.7 * inch, 0.6 * inch, 1.2 * inch, 1.2 * inch])
            
            # Apply Alternating row backgrounds and headers
            table_style_list = [
                ('BACKGROUND', (0,0), (-1,0), primary_color),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('GRID', (0,0), (-1,-1), 0.5, line_color),
            ]
            
            # Alternating row background for rows after header
            for idx in range(1, len(item_data)):
                if idx % 2 == 0:
                    table_style_list.append(('BACKGROUND', (0, idx), (-1, idx), light_bg_color))
            
            items_table.setStyle(TableStyle(table_style_list))
            
            story.append(Paragraph("<b>BILL DETAILS</b>", section_heading_style))
            story.append(Spacer(1, 5))
            story.append(items_table)
            story.append(Spacer(1, 15))

            # --- Summary Section (Subtotal, Discount, Grand Total) ---
            summary_data = [
                ["", "", Paragraph("Subtotal:", summary_label_style), Paragraph(f"Rs {bill_data['subtotal']:.2f}", summary_value_style)],
                ["", "", Paragraph("Discount:", summary_label_style), Paragraph(f"Rs {bill_data['discount']:.2f}", summary_value_style)],
                ["", "", Paragraph("Grand Total:", summary_label_style), Paragraph(f"Rs {bill_data['grand_total']:.2f}", summary_value_style)]
            ]
            summary_table = Table(summary_data, colWidths=[1.8 * inch, 2.7 * inch, 1.5 * inch, 1.5 * inch])
            summary_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LINEBELOW', (2,0), (3,0), 0.5, line_color),
                ('LINEBELOW', (2,1), (3,1), 0.5, line_color),
                ('LINEBELOW', (2,2), (3,2), 1.5, primary_color),
                ('TOPPADDING', (2,0), (-1,-1), 4),
                ('BOTTOMPADDING', (2,0), (-1,-1), 4),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 40))

            # Define footer draw callback to place the footer at the absolute bottom of the page
            # def draw_footer(canvas, document):
            #     canvas.saveState()
            #     canvas.setFont('Helvetica-BoldOblique', 10)
            #     canvas.setFillColor(primary_color)
            #     # Centered horizontally at 612/2 (letter width is 8.5" * 72 = 612 pt) and 30 pt from the bottom
            #     canvas.drawCentredString(612 / 2.0, 30, invoice_footer)
            #     canvas.restoreState()

            # Build PDF with footer callback
            # doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
            # logger.info(f"Successfully generated invoice PDF at: {pdf_path}")
            # return pdf_path

        except Exception as e:
            logger.error(f"Failed to generate invoice PDF: {str(e)}")
            return None
