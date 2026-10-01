# 🏥 OPD Billing & Clinic Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52.svg)](https://pypi.org/project/PyQt6/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![Status](https://img.shields.io/badge/Status-Production--Ready-success.svg)](#)

A modern, desktop-based **Outpatient Department (OPD) Medical Billing & Clinic Management System** built with **Python** and **PyQt6**. Designed specifically for healthcare centers, outpatient clinics, and diagnostic labs, this application streamlines patient registration, consultation appointments, diagnostic test ordering, point-of-sale billing, thermal receipt printing, and revenue reporting.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Architecture & Design](#-architecture--design)
- [Screenshots & UI Showcase](#-screenshots--ui-showcase)
- [Repository Structure](#-repository-structure)
- [Tech Stack & Libraries](#-tech-stack--libraries)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [Author & License](#-author--license)

---

## ✨ Key Features

### 1. 💳 Fast Point-of-Sale (POS) Counter Billing
- Multi-item invoice generation covering doctor consultations, specialized clinical procedures, and pathology/lab tests.
- Real-time total, subtotal, and tax calculations with flexible discount support (percentage or fixed value).
- Instant invoice generation with automated receipt numbering and transaction logging.

### 2. 🖨️ Thermal Receipt & PDF Invoice Printing
- Direct hardware integration with **58mm and 80mm thermal receipt printers** via ESC/POS utilities.
- Publication-quality A4/A5 PDF invoices and receipt generation using **ReportLab**, featuring clinic branding, patient details, and itemized fee breakdowns.

### 3. 👥 Patient & Records Management
- Patient registration with demographics, contact details, and visit tracking.
- Instant search by Patient MR/ID, Name, or Phone number.
- Comprehensive visit history and historical billing records retrieval.

### 4. 🩺 Doctor & Specialty Registry
- Complete directory of visiting and resident physicians.
- Department assignments and automated consultation fee scheduling.

### 5. 🧪 Pathology & Diagnostic Tests Management
- Built-in diagnostic lab test catalog with categorized pricing and sample collection details.
- Supports bulk pricing synchronization from Excel datasets (e.g., `CDC Wah Pathology Rate List.xlsx`).

### 6. 📈 Financial Analytics & Visual Reports
- Interactive financial dashboard displaying daily collections, monthly revenue, patient footfall, and top-prescribed tests.
- Visual charts and revenue breakdown plots generated with **Matplotlib**.
- One-click export of detailed audit summaries to Microsoft Excel (`.xlsx`) via **OpenPyXL** and **Pandas**.

### 7. 🎨 Modern Ergonomic User Interface
- Polished desktop UI built in **PyQt6** following contemporary healthcare UI/UX guidelines.
- Dynamic **Light Mode & Dark Mode** switching with custom palette tokens (Slate & Hospital Blue).
- Non-intrusive animated toast notifications and custom card widgets.

---

## 🏛️ Architecture & Design

The application follows the **Model-View-Controller (MVC)** architectural pattern to ensure separation of concerns, scalability, and ease of maintenance:

```text
┌─────────────────┐       User Input       ┌─────────────────────┐
│      Views      │ ─────────────────────> │     Controllers     │
│ (PyQt6 Screens) │ <───────────────────── │  (Business Logic)   │
└─────────────────┘      Data Binding      └──────────┬──────────┘
                                                      │
                                                      ▼
                                           ┌─────────────────────┐
                                           │    Models & SQLite  │
                                           │  (Database Manager) │
                                           └─────────────────────┘
```

---

## 📂 Repository Structure

```text
OPD-Billing-System/
├── controllers/                   # Application business logic
│   ├── billing_controller.py      # Cart, calculations, and checkout logic
│   ├── main_controller.py         # Route navigation & coordinator
│   └── reports_controller.py      # Analytics & export generation
├── database/                      # Data persistence layer
│   └── db_manager.py              # SQLite connection, schemas & migrations
├── models/                        # Object-Relational Data Entities
│   ├── bill.py                    # Invoice and transaction schema
│   ├── doctor.py                  # Physician schema & fee schedules
│   ├── lab_test.py                # Diagnostic tests catalog
│   ├── patient.py                 # Patient demographics & history
│   ├── procedure.py               # Medical procedures catalog
│   └── user.py                    # Staff & administrator authentication
├── views/                         # PyQt6 Graphical User Interfaces
│   ├── billing_view.py            # Point-of-sale checkout screen
│   ├── dashboard_view.py          # Summary analytics & KPI cards
│   ├── doctor_view.py             # Doctor directory & fee management
│   ├── history_view.py            # Past bills & invoice lookup
│   ├── lab_test_view.py           # Pathology test pricing catalog
│   ├── login_view.py              # Authentication window
│   ├── main_window.py             # Main application shell & sidebar
│   ├── patient_records_view.py    # Complete clinical patient records
│   ├── patient_view.py            # Patient registration & queue
│   ├── procedure_view.py          # Clinical procedures management
│   ├── reports_view.py            # Financial reports & graphs
│   ├── settings_view.py           # System, clinic & printer settings
│   └── widgets/                   # Custom reusable UI cards, charts & toasts
├── utils/                         # Reusable helpers & hardware drivers
│   ├── logger.py                  # Rotating file and console logger
│   ├── pdf_generator.py           # ReportLab PDF invoice builder
│   └── printer.py                 # Thermal printer interface
├── CDC Wah Pathology Rate List.xlsx # Preloaded diagnostic rate list
├── config.py                      # Global styling tokens, fonts & config
├── main.py                        # Application entrypoint & coordinator
└── requirements.txt               # Python package dependencies
```

---

## 🛠️ Tech Stack & Libraries

- **Language:** Python 3.10+
- **GUI Framework:** PyQt6
- **Database:** SQLite3
- **PDF Generation:** ReportLab
- **Excel & Data:** Pandas, OpenPyXL
- **Visualization:** Matplotlib

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10 or higher** installed.

### 2. Clone the Repository
```bash
git clone https://github.com/muhammadumerrafiq/OPD-Billing-System.git
cd OPD-Billing-System
```

### 3. Create a Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
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

The database schema and initial test catalog will be automatically initialized on first run.

---

## ⚙️ Configuration

Application settings, branding, colors, and typography can be customized in `config.py`:

```python
class AppConfig:
    COLOR_PRIMARY = "#0F6CBD"      # Hospital Deep Blue
    COLOR_SECONDARY = "#38BDF8"    # Sky Blue
    FONT_PRIMARY = "Outfit"        # Main Typography
    FONT_SECONDARY = "Segoe UI"    # Secondary Typography
```

Printer configuration (receipt width, COM port / USB, paper cut triggers) can be configured via `utils/printer.py` or through the in-app **Settings View**.

---

## 👤 Author & License

- **Developer:** [Muhammad Umer Rafiq](https://github.com/muhammadumerrafiq)
- **License:** Open-sourced under the [MIT License](LICENSE).
