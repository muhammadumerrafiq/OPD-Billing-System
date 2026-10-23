# 🏥 OPD Billing & Clinic Management System

<p align="center">
  <img src="logo.jpeg" alt="OPD Billing System Logo" width="130" style="border-radius: 12px;" />
</p>

<p align="center">
  <strong>Desktop Outpatient Department (OPD) Medical Billing & Clinic Management Solution</strong>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=flat&logo=python&logoColor=white" alt="Python 3.10+" /></a>
  <a href="https://pypi.org/project/PyQt6/"><img src="https://img.shields.io/badge/GUI-PyQt6-41CD52.svg?style=flat&logo=qt&logoColor=white" alt="PyQt6" /></a>
  <a href="https://www.sqlite.org/"><img src="https://img.shields.io/badge/Database-SQLite3-003B57.svg?style=flat&logo=sqlite&logoColor=white" alt="SQLite3" /></a>
  <a href="https://pandas.pydata.org/"><img src="https://img.shields.io/badge/Data-Pandas%20%7C%20OpenPyXL-150458.svg?style=flat&logo=pandas&logoColor=white" alt="Pandas" /></a>
  <a href="https://matplotlib.org/"><img src="https://img.shields.io/badge/Charts-Matplotlib-11557c.svg?style=flat" alt="Matplotlib" /></a>
  <a href="https://www.reportlab.com/"><img src="https://img.shields.io/badge/Reports-ReportLab%20PDF-D32F2F.svg?style=flat" alt="ReportLab" /></a>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg?style=flat" alt="Cross Platform" />
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat" alt="License" />
</p>

---

## 📖 Overview

The **OPD Billing & Clinic Management System** is a high-performance desktop application engineered with **Python** and **PyQt6**. Designed specifically for hospitals, polyclinics, diagnostic pathology laboratories, and outpatient dispensaries (including centers like *Bismel Medical Center* and *CDC Wah*), this system streamlines daily reception counters, doctor consultations, lab test ordering, Point-of-Sale (POS) cash invoicing, thermal receipt generation, and revenue auditing.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Module Highlights](#-module-highlights)
- [Repository Structure](#-repository-structure)
- [Tech Stack & Dependencies](#-tech-stack--dependencies)
- [Getting Started](#-getting-started)
- [Hardware & Configuration](#-hardware--configuration)
- [Author & License](#-author--license)

---

## ✨ Key Features

### 1. 💳 Fast Point-of-Sale (POS) Counter Checkout
- Rapid itemized cart builder for doctor consultations, clinical procedures, and diagnostic pathology tests.
- Real-time subtotal, discount (percentage or flat discount), and net payable calculations.
- Instant checkout generating uniquely sequenced MR and invoice serial numbers.

### 2. 🖨️ ESC/POS Thermal Printing & PDF Invoicing
- Direct hardware driver support for standard **58mm and 80mm ESC/POS thermal receipt printers**.
- Automated paper cut, custom header/footer clinic branding, and receipt reprint capabilities.
- Publication-grade **A4/A5 PDF invoices** generated via **ReportLab** for insurance and medical records.

### 3. 👥 Patient Directory & Visit History
- Patient demographic tracking with unique Medical Record (MR) number assignment.
- Instant search by MR ID, patient name, or contact number.
- Patient visit timeline and previous invoice history retrieval.

### 4. 🩺 Physician Registry & Fee Scheduling
- Centralized doctor directory with specialty and department assignments.
- Configurable doctor consultation fees and commission tracking.

### 5. 🧪 Diagnostic Pathology Tests Catalog
- Pre-configured diagnostic lab test database with category classifications.
- Integrated rate synchronization supporting Excel imports (e.g., `CDC Wah Pathology Rate List.xlsx`).

### 6. 📈 Financial Reports & Executive Analytics
- Real-time financial dashboard displaying today's collections, monthly revenue, and patient footfall.
- Embedded **Matplotlib** charts visualizing income streams and high-volume test procedures.
- One-click export of structured financial and audit logs to Excel (`.xlsx`) via **Pandas** and **OpenPyXL**.

### 7. 🎨 Ergonomic PyQt6 Interface
- Custom medical-grade theme with smooth toggle between **Light Mode** and **Dark Mode**.
- Responsive sidebar navigation, non-blocking animated toast notifications, and keyboard shortcuts.

---

## 🏛️ System Architecture

The application adopts the **Model-View-Controller (MVC)** architectural pattern to ensure clean separation of UI components, business logic, and database persistence:

```text
┌─────────────────────────────────┐
│           PyQt6 Views           │  <--- Desktop GUI & User Interaction
│ (Billing, Dashboard, Patients)  │
└────────────────┬────────────────┘
                 │ (Events / Signals)
                 ▼
┌─────────────────────────────────┐
│           Controllers           │  <--- Cart Calculations, POS Checkout,
│ (Billing, Reports, Navigation)  │       Validation & Business Logic
└────────────────┬────────────────┘
                 │ (Queries & Transactions)
                 ▼
┌─────────────────────────────────┐
│     Models & SQLite Manager     │  <--- Relational Schema, Migrations
│ (Bill, Patient, Doctor, Lab)    │       and File Persistence
└─────────────────────────────────┘
```

---

## 📂 Repository Structure

```text
OPD-Billing-System/
├── controllers/                   # Application business logic & event handlers
│   ├── billing_controller.py      # Cart operations, totals, and POS transactions
│   ├── main_controller.py         # View coordination & window routing
│   └── reports_controller.py      # Financial aggregation & Excel export logic
├── database/                      # Data persistence layer
│   └── db_manager.py              # SQLite connection pool, tables & migrations
├── models/                        # Relational data entities
│   ├── bill.py                    # Invoice and transaction schema
│   ├── doctor.py                  # Physician profiles & fee structures
│   ├── lab_test.py                # Diagnostic test records
│   ├── patient.py                 # Patient demographics & MR schema
│   ├── procedure.py               # Medical procedures catalog
│   └── user.py                    # Operator credentials & role management
├── views/                         # PyQt6 Graphical User Interface screens
│   ├── billing_view.py            # Point-of-sale checkout counter
│   ├── dashboard_view.py          # KPI metrics & quick action cards
│   ├── doctor_view.py             # Doctor management panel
│   ├── history_view.py            # Invoice archive & reprints
│   ├── lab_test_view.py           # Pathology catalog editor
│   ├── login_view.py              # User authentication screen
│   ├── main_window.py             # Main application window & responsive sidebar
│   ├── patient_records_view.py    # Detailed patient clinical records
│   ├── patient_view.py            # Patient registration & queue
│   ├── procedure_view.py          # Clinical procedures manager
│   ├── reports_view.py            # Revenue graphs & audit reports
│   ├── settings_view.py           # Hardware, clinic & thermal printer configuration
│   └── widgets/                   # Reusable UI cards, SVG icons, and toast alerts
├── utils/                         # Helper modules & hardware integration
│   ├── logger.py                  # Log rotation & debugging utilities
│   ├── pdf_generator.py           # ReportLab PDF invoice builder
│   └── printer.py                 # ESC/POS thermal printer driver
├── CDC Wah Pathology Rate List.xlsx # Preloaded diagnostic rate list
├── config.py                      # Theme tokens, fonts, and global settings
├── logo.jpeg                      # Clinic branding asset
├── main.py                        # Application entrypoint
└── requirements.txt               # Python package dependencies
```

---

## 🛠️ Tech Stack & Dependencies

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | [Python 3.10+](https://www.python.org/) | Core language runtime |
| **GUI Framework** | [PyQt6](https://pypi.org/project/PyQt6/) | Desktop user interface and event handling |
| **Database** | [SQLite3](https://www.sqlite.org/) | Local, zero-configuration relational persistence |
| **PDF Generation** | [ReportLab](https://www.reportlab.com/) | Publication-ready invoices and receipt PDFs |
| **Data Processing** | [Pandas](https://pandas.pydata.org/) & [OpenPyXL](https://openpyxl.readthedocs.io/) | Excel rate sheet parsing and financial exports |
| **Visualization** | [Matplotlib](https://matplotlib.org/) | Analytical charts and trend graphs |
| **Hardware Driver** | Custom ESC/POS implementation | Thermal receipt printing (58mm / 80mm) |

---

## 🚀 Getting Started

### 1. Prerequisites

Ensure you have **Python 3.10 or higher** installed. Verify with:
```bash
python --version
```

### 2. Clone the Repository

```bash
git clone https://github.com/muhammadumerrafiq/OPD-Billing-System.git
cd OPD-Billing-System
```

### 3. Setup Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Launch the Application

```bash
python main.py
```

> **Note:** On the first execution, SQLite will automatically initialize the database schema and load necessary initial test catalogs.

---

## ⚙️ Hardware & Configuration

### Application Styling & Branding
Colors, typography, and styling variables can be adjusted in [`config.py`](config.py):
```python
class AppConfig:
    COLOR_PRIMARY = "#0F6CBD"      # Hospital Deep Blue
    COLOR_SECONDARY = "#38BDF8"    # Sky Blue
    FONT_PRIMARY = "Outfit"        # Primary Font
    FONT_SECONDARY = "Segoe UI"    # Secondary Font
```

### Thermal Printer Settings
ESC/POS thermal printer properties (paper width, baud rate, USB/Serial port name, and auto-cutter) can be configured via [`utils/printer.py`](utils/printer.py) or directly from the in-app **Settings View**.

---

## 👤 Author & License

- **Developer & Maintainer:** [Muhammad Umer Rafiq](https://github.com/muhammadumerrafiq)
- **License:** Open-sourced under the [MIT License](https://opensource.org/licenses/MIT).
