from datetime import datetime
from database.db_manager import DatabaseManager
from utils.logger import logger

class Bill:
    @staticmethod
    def generate_next_invoice_number():
        """Generates the next sequential invoice number for the current year.
        Format: INV-YYYY-XXXXX (e.g., INV-2026-00001)
        """
        db = DatabaseManager()
        current_year = datetime.now().year
        search_pattern = f"INV-{current_year}-%"
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM bills WHERE invoice_number LIKE ?;", (search_pattern,))
                count = cursor.fetchone()[0]
                next_seq = count + 1
                return f"INV-{current_year}-{next_seq:05d}"
        except Exception as e:
            logger.error(f"Error generating invoice number: {str(e)}")
            return f"INV-{current_year}-00001"

    @staticmethod
    def create_bill(patient_id, subtotal, discount, grand_total, payment_method, items):
        """Creates a new bill and its line items inside a single transaction.
        Returns the generated invoice number if successful, else None.
        """
        db = DatabaseManager()
        invoice_number = Bill.generate_next_invoice_number()
        created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                # Insert bill
                cursor.execute("""
                    INSERT INTO bills (invoice_number, patient_id, subtotal, discount, grand_total, payment_method, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (invoice_number, patient_id, subtotal, discount, grand_total, payment_method, created_date))

                bill_id = cursor.lastrowid

                # Insert bill items
                for item in items:
                    cursor.execute("""
                        INSERT INTO bill_items (bill_id, item_name, category, quantity, price, total)
                        VALUES (?, ?, ?, ?, ?, ?);
                    """, (
                        bill_id,
                        item.get('item_name'),
                        item.get('category'),
                        item.get('quantity', 1),
                        item.get('price', 0.0),
                        item.get('total', 0.0)
                    ))

                conn.commit()
                logger.info(f"Saved bill {invoice_number} (ID: {bill_id}) for patient {patient_id}.")
                return invoice_number
        except Exception as e:
            logger.error(f"Error saving bill: {str(e)}")
            return None

    @staticmethod
    def delete_bill(bill_id):
        """Deletes a bill. Cascade deletes items due to foreign key constraints."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM bills WHERE bill_id = ?;", (bill_id,))
                conn.commit()
                logger.info(f"Deleted bill ID: {bill_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete bill ID {bill_id}: {str(e)}")
            return False

    @staticmethod
    def get_bill_by_invoice(invoice_number):
        """Retrieves a single bill and all its items by invoice number."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                # Fetch bill and patient details
                cursor.execute("""
                    SELECT b.*, p.patient_name, p.father_name, p.gender, p.age, p.phone, p.cnic, p.address
                    FROM bills b
                    JOIN patients p ON b.patient_id = p.patient_id
                    WHERE b.invoice_number = ?;
                """, (invoice_number,))
                bill_row = cursor.fetchone()
                if not bill_row:
                    return None

                bill_data = dict(bill_row)

                # Fetch bill items
                cursor.execute("""
                    SELECT * FROM bill_items WHERE bill_id = ?;
                """, (bill_data['bill_id'],))
                items_rows = cursor.fetchall()
                bill_data['items'] = [dict(item) for item in items_rows]

                return bill_data
        except Exception as e:
            logger.error(f"Failed to fetch bill by invoice {invoice_number}: {str(e)}")
            return None

    @staticmethod
    def get_all_bills(limit=1000):
        """Returns all bills with patient names."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT b.*, p.patient_name
                    FROM bills b
                    JOIN patients p ON b.patient_id = p.patient_id
                    ORDER BY b.bill_id DESC
                    LIMIT ?;
                """, (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching all bills: {str(e)}")
            return []

    @staticmethod
    def search_bills(search_query):
        """Searches bills by invoice number, patient name, or patient ID."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                term = f"%{search_query}%"
                cursor.execute("""
                    SELECT b.*, p.patient_name
                    FROM bills b
                    JOIN patients p ON b.patient_id = p.patient_id
                    WHERE b.invoice_number LIKE ? OR p.patient_name LIKE ? OR b.patient_id LIKE ?
                    ORDER BY b.bill_id DESC;
                """, (term, term, term))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error searching bills: {str(e)}")
            return []

    # --- Analytics & Reports Queries ---

    @staticmethod
    def get_today_revenue():
        """Returns today's total revenue (grand total sum)."""
        db = DatabaseManager()
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(grand_total) FROM bills WHERE date(created_date) = date(?);", (today,))
                row = cursor.fetchone()
                return row[0] if row[0] is not None else 0.0
        except Exception as e:
            logger.error(f"Error getting today's revenue: {str(e)}")
            return 0.0

    @staticmethod
    def get_today_bills_count():
        """Returns the number of bills created today."""
        db = DatabaseManager()
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM bills WHERE date(created_date) = date(?);", (today,))
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting today's bills count: {str(e)}")
            return 0

    @staticmethod
    def get_revenue_summary():
        """Returns high-level statistics for dashboard widgets."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(grand_total), COUNT(*) FROM bills;")
                row = cursor.fetchone()
                total_rev = row[0] if row[0] is not None else 0.0
                total_bills = row[1] if row[1] is not None else 0
                return total_rev, total_bills
        except Exception as e:
            logger.error(f"Error getting revenue summary: {str(e)}")
            return 0.0, 0

    @staticmethod
    def get_daily_registrations_chart_data(days_limit=7):
        """Returns patient registration counts for the last N days."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT date(registration_date) as reg_date, COUNT(*)
                    FROM patients
                    GROUP BY reg_date
                    ORDER BY reg_date DESC
                    LIMIT ?;
                """, (days_limit,))
                rows = cursor.fetchall()
                # Reverse to sort in chronological order
                data = [(row[0], row[1]) for row in rows]
                data.reverse()
                return data
        except Exception as e:
            logger.error(f"Error getting daily registrations chart data: {str(e)}")
            return []

    @staticmethod
    def get_daily_revenue_chart_data(days_limit=7):
        """Returns revenue values for the last N days."""
        db = DatabaseManager()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT date(created_date) as bill_date, SUM(grand_total)
                    FROM bills
                    GROUP BY bill_date
                    ORDER BY bill_date DESC
                    LIMIT ?;
                """, (days_limit,))
                rows = cursor.fetchall()
                data = [(row[0], row[1]) for row in rows]
                data.reverse()
                return data
        except Exception as e:
            logger.error(f"Error getting daily revenue chart data: {str(e)}")
            return []

    @staticmethod
    def get_monthly_revenue_report(year=None):
        """Returns revenue grouped by month for the selected year."""
        db = DatabaseManager()
        if not year:
            year = datetime.now().year
        search_pattern = f"{year}-%"
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT strftime('%m', created_date) as month_num, SUM(grand_total), COUNT(*)
                    FROM bills
                    WHERE created_date LIKE ?
                    GROUP BY month_num
                    ORDER BY month_num ASC;
                """, (search_pattern,))
                rows = cursor.fetchall()
                months_map = {
                    "01": "January", "02": "February", "03": "March", "04": "April",
                    "05": "May", "06": "June", "07": "July", "08": "August",
                    "09": "September", "10": "October", "11": "November", "12": "December"
                }
                result = []
                for row in rows:
                    m_num, total, count = row
                    result.append({
                        "month": months_map.get(m_num, m_num),
                        "revenue": total,
                        "bills_count": count
                    })
                return result
        except Exception as e:
            logger.error(f"Error getting monthly revenue report: {str(e)}")
            return []

    @staticmethod
    def get_doctor_wise_revenue_report(start_date=None, end_date=None):
        """Returns revenue generated by doctor consultations."""
        db = DatabaseManager()
        query = """
            SELECT bi.item_name as doctor_name, SUM(bi.total) as total_revenue, COUNT(*) as consultation_count
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.bill_id
            WHERE bi.category = 'Doctor Consultation'
        """
        params = []
        if start_date and end_date:
            query += " AND date(b.created_date) BETWEEN date(?) AND date(?)"
            params.extend([start_date, end_date])
        query += " GROUP BY bi.item_name ORDER BY total_revenue DESC;"

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting doctor-wise revenue report: {str(e)}")
            return []

    @staticmethod
    def get_procedure_revenue_report(start_date=None, end_date=None):
        """Returns revenue generated by procedures, indicating name and category."""
        db = DatabaseManager()
        query = """
            SELECT bi.item_name as procedure_name, p.category, SUM(bi.total) as total_revenue, SUM(bi.quantity) as quantity_sold
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.bill_id
            LEFT JOIN procedures p ON bi.item_name = p.procedure_name
            WHERE bi.category = 'Procedure'
        """
        params = []
        if start_date and end_date:
            query += " AND date(b.created_date) BETWEEN date(?) AND date(?)"
            params.extend([start_date, end_date])
        query += " GROUP BY bi.item_name, p.category ORDER BY total_revenue DESC;"

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting procedure revenue report: {str(e)}")
            return []

    @staticmethod
    def get_lab_revenue_report(start_date=None, end_date=None):
        """Returns revenue generated by laboratory tests."""
        db = DatabaseManager()
        query = """
            SELECT bi.item_name as test_name, SUM(bi.total) as total_revenue, SUM(bi.quantity) as quantity_sold
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.bill_id
            WHERE bi.category = 'Lab Test'
        """
        params = []
        if start_date and end_date:
            query += " AND date(b.created_date) BETWEEN date(?) AND date(?)"
            params.extend([start_date, end_date])
        query += " GROUP BY bi.item_name ORDER BY total_revenue DESC;"

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting lab revenue report: {str(e)}")
            return []

    @staticmethod
    def get_general_revenue_report(start_date=None, end_date=None):
        """Returns general revenue details for a specific date range."""
        db = DatabaseManager()
        query = """
            SELECT date(created_date) as transaction_date, SUM(subtotal) as subtotal_sum, SUM(discount) as discount_sum, SUM(grand_total) as grand_total_sum, COUNT(*) as bills_count
            FROM bills
        """
        params = []
        if start_date and end_date:
            query += " WHERE date(created_date) BETWEEN date(?) AND date(?)"
            params.extend([start_date, end_date])
        query += " GROUP BY transaction_date ORDER BY transaction_date DESC;"

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting general revenue report: {str(e)}")
            return []
