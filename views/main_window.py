from PyQt6.QtWidgets import QMainWindow, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel, QSpacerItem, QSizePolicy, QToolButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
from config import AppConfig
from views.widgets.svg_icon import SVGIconFactory
from views.widgets.toast import ToastNotification
from utils.logger import logger

class MainWindow(QMainWindow):
    # Signals for page changes and logout
    page_changed = pyqtSignal(str)
    logout_requested = pyqtSignal()
    theme_toggled = pyqtSignal(bool)

    def __init__(self, current_user, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.is_dark = is_dark_mode
        self.sidebar_buttons = {}

        self.setWindowTitle("Bismel Medical Center - OPD Billing Management System")
        self.resize(1280, 800)
        self.setup_ui()

    def setup_ui(self):
        # Central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Main Layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Left Sidebar
        self.setup_sidebar()

        # 2. Right Container (Header + Content Stack)
        self.content_container = QWidget(self)
        self.container_layout = QVBoxLayout(self.content_container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)

        # Header
        self.setup_header()

        # Main Content Stack
        self.content_stack = QStackedWidget(self)
        self.container_layout.addWidget(self.content_stack, 1)

        self.main_layout.addWidget(self.content_container, 1)

        # Apply design system styles
        self.apply_theme_styling()

    def setup_sidebar(self):
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("SidebarFrame")
        self.sidebar_frame.setFixedWidth(240)

        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(8)

        # Sidebar Header (Hospital Branding Logo + Name)
        brand_layout = QHBoxLayout()
        brand_layout.setContentsMargins(20, 10, 20, 20)
        brand_layout.setSpacing(10)

        self.brand_icon = QLabel()
        brand_layout.addWidget(self.brand_icon)

        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(2)
        
        self.brand_name_label = QLabel("Bismel Medical")
        self.brand_name_label.setFont(QFont(AppConfig.FONT_PRIMARY, 13, QFont.Weight.Bold))
        self.brand_name_label.setStyleSheet("color: #0F6CBD;")
        brand_text_layout.addWidget(self.brand_name_label)

        self.brand_sub_label = QLabel("Center - OPD")
        self.brand_sub_label.setFont(QFont(AppConfig.FONT_PRIMARY, 9, QFont.Weight.Medium))
        self.brand_sub_label.setStyleSheet("color: #64748B;")
        brand_text_layout.addWidget(self.brand_sub_label)

        brand_layout.addLayout(brand_text_layout, 1)
        sidebar_layout.addLayout(brand_layout)

        # Separator line
        self.sidebar_sep = QFrame()
        self.sidebar_sep.setFrameShape(QFrame.Shape.HLine)
        self.sidebar_sep.setFrameShadow(QFrame.Shadow.Sunken)
        self.sidebar_sep.setStyleSheet("background-color: transparent;") # will set border via QSS
        sidebar_layout.addWidget(self.sidebar_sep)
        sidebar_layout.addSpacing(10)

        # Sidebar Menu Items
        # format: (key, display_name, icon_name)
        menu_items = [
            ("dashboard", "Dashboard", "dashboard"),
            ("patient_reg", "Register Patient", "patients_reg"),
            ("patient_rec", "Patient Records", "patients_rec"),
            ("doctors", "Manage Doctors", "doctors"),
            ("procedures", "Manage Procedures", "procedures"),
            ("lab_tests", "Manage Lab Tests", "lab_tests"),
            ("billing", "Create Bill", "billing"),
            ("history", "Invoice History", "history"),
            ("reports", "Reports & Analytics", "reports"),
            ("settings", "Settings", "settings")
        ]

        for key, name, icon_name in menu_items:
            btn = QPushButton(name)
            btn.setObjectName("SidebarBtn")
            btn.setCheckable(True)
            btn.setMinimumHeight(44)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Save mapping
            self.sidebar_buttons[key] = {
                "button": btn,
                "icon_name": icon_name
            }
            
            # Action connect
            btn.clicked.connect(lambda checked, k=key: self.navigate_to_page(k))
            sidebar_layout.addWidget(btn)

        # Spacer to push logout button to the bottom
        sidebar_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Logout Button
        self.logout_btn = QPushButton("Sign Out")
        self.logout_btn.setObjectName("SidebarBtn")
        self.logout_btn.setMinimumHeight(44)
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        sidebar_layout.addWidget(self.logout_btn)

        self.main_layout.addWidget(self.sidebar_frame)

        # Handle Role-Based Permissions
        self.apply_role_permissions()

    def setup_header(self):
        self.header_frame = QFrame()
        self.header_frame.setMinimumHeight(64)
        self.header_frame.setMaximumHeight(64)
        
        # Bottom border for header
        self.header_frame.setStyleSheet("""
            QFrame {
                border-bottom: 1.5px solid rgba(226, 232, 240, 0.8);
                background-color: transparent;
            }
        """)

        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(25, 0, 25, 0)
        header_layout.setSpacing(15)

        # Current view title label
        self.page_title_label = QLabel("Dashboard")
        self.page_title_label.setObjectName("TitleLabel")
        header_layout.addWidget(self.page_title_label)

        header_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # User details card
        user_info_layout = QHBoxLayout()
        user_info_layout.setSpacing(6)
        
        self.user_role_label = QLabel(f"{self.current_user.full_name} ({self.current_user.role})")
        self.user_role_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.user_role_label.setStyleSheet("color: #64748B;")
        
        # User icon
        self.user_icon_label = QLabel()
        user_info_layout.addWidget(self.user_icon_label)
        user_info_layout.addWidget(self.user_role_label)
        header_layout.addLayout(user_info_layout)

        # Theme Switcher Tool Button
        self.theme_btn = QToolButton()
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setFixedSize(36, 36)
        self.theme_btn.setStyleSheet("""
            QToolButton {
                border: 1px solid rgba(226, 232, 240, 0.8);
                border-radius: 18px;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: rgba(226, 232, 240, 0.4);
            }
        """)
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn)

        self.container_layout.addWidget(self.header_frame)

    def apply_role_permissions(self):
        """Disables/hides administrative sections for receptionists."""
        if self.current_user.role == "Receptionist":
            admin_sections = ["doctors", "procedures", "lab_tests", "reports"]
            for section in admin_sections:
                if section in self.sidebar_buttons:
                    self.sidebar_buttons[section]["button"].setVisible(False)
            logger.info("Hidden administrative sidebar options for Receptionist.")

    def apply_theme_styling(self):
        # Set primary styles on main window & container
        self.central_widget.setStyleSheet(AppConfig.get_stylesheet(self.is_dark))
        
        # Border adjustments for frames in dark mode
        border_color = AppConfig.COLOR_DARK_BORDER if self.is_dark else AppConfig.COLOR_LIGHT_BORDER
        text_color = AppConfig.COLOR_DARK_TEXT if self.is_dark else AppConfig.COLOR_LIGHT_TEXT
        muted_color = AppConfig.COLOR_DARK_MUTED if self.is_dark else AppConfig.COLOR_LIGHT_MUTED

        self.header_frame.setStyleSheet(f"""
            QFrame {{
                border-bottom: 1.5px solid {border_color};
                background-color: transparent;
            }}
            QLabel {{
                border: none;
            }}
        """)
        
        self.sidebar_frame.setStyleSheet(f"""
            QFrame#SidebarFrame {{
                background-color: {"#1E293B" if self.is_dark else "#FFFFFF"};
                border-right: 1.5px solid {border_color};
            }}
        """)
        
        self.sidebar_sep.setStyleSheet(f"background-color: {border_color}; max-height: 1px; min-height: 1px;")
        self.brand_name_label.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")
        self.brand_sub_label.setStyleSheet(f"color: {muted_color};")
        self.user_role_label.setStyleSheet(f"color: {muted_color};")
        self.page_title_label.setStyleSheet(f"color: {AppConfig.COLOR_PRIMARY};")

        # Icons update
        import os
        import sys
        if getattr(sys, 'frozen', False):
            logo_path = os.path.join(sys._MEIPASS, "logo.jpeg")
        else:
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logo_path = os.path.join(project_dir, "logo.jpeg")
        if os.path.exists(logo_path):
            pix_brand = QPixmap(logo_path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.brand_icon.setPixmap(pix_brand)
        else:
            brand_color = AppConfig.COLOR_PRIMARY
            pix_brand = SVGIconFactory.get_pixmap("doctors", color=brand_color, size=(28, 28))
            self.brand_icon.setPixmap(pix_brand)

        pix_user = SVGIconFactory.get_pixmap("patients_rec", color=muted_color, size=(18, 18))
        self.user_icon_label.setPixmap(pix_user)

        # Update Theme Switcher Icon
        theme_icon_name = "sun" if self.is_dark else "moon"
        theme_icon_color = "#38BDF8" if self.is_dark else "#1E293B"
        theme_pix = SVGIconFactory.get_pixmap(theme_icon_name, color=theme_icon_color, size=(18, 18))
        self.theme_btn.setIcon(QIcon(theme_pix))
        self.theme_btn.setIconSize(QSize(18, 18))
        self.theme_btn.setStyleSheet(f"""
            QToolButton {{
                border: 1.5px solid {border_color};
                border-radius: 18px;
                background-color: transparent;
            }}
            QToolButton:hover {{
                background-color: {"rgba(255, 255, 255, 0.08)" if self.is_dark else "rgba(0, 0, 0, 0.05)"};
            }}
        """)

        # Sidebar Buttons Icons update
        for key, value in self.sidebar_buttons.items():
            btn = value["button"]
            icon_name = value["icon_name"]
            
            # Checked buttons have primary color icon, others have muted color
            active_color = AppConfig.COLOR_PRIMARY if btn.isChecked() else muted_color
            btn_icon = SVGIconFactory.get_icon(icon_name, color=active_color, size=(18, 18))
            btn.setIcon(btn_icon)
            btn.setIconSize(QSize(18, 18))

        # Logout button icon
        logout_icon = SVGIconFactory.get_icon("logout", color=muted_color, size=(18, 18))
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QSize(18, 18))

    def navigate_to_page(self, key):
        """Switches stack views and changes button checked states."""
        # Uncheck other buttons
        for k, val in self.sidebar_buttons.items():
            val["button"].setChecked(k == key)
        
        # Trigger icon repaint based on new selection colors
        self.apply_theme_styling()

        # Update page title in header
        page_names = {
            "dashboard": "Dashboard",
            "patient_reg": "Register Patient",
            "patient_rec": "Patient Records",
            "doctors": "Doctors Management",
            "procedures": "Procedures Management",
            "lab_tests": "Lab Tests Management",
            "billing": "New Invoice / Billing",
            "history": "Invoice History",
            "reports": "Reports & Analytics",
            "settings": "System Settings"
        }
        self.page_title_label.setText(page_names.get(key, "System"))

        # Emit change signal to controller to handle QStackedWidget index
        self.page_changed.emit(key)

    def register_view(self, key, widget):
        """Adds a view to the QStackedWidget."""
        self.content_stack.addWidget(widget)

    def show_view(self, widget):
        """Switches content stack to show a specific widget."""
        self.content_stack.setCurrentWidget(widget)

    def toggle_theme(self):
        """Toggles Light and Dark Theme."""
        self.is_dark = not self.is_dark
        self.theme_toggled.emit(self.is_dark)
        self.apply_theme_styling()
        # Trigger toast notification
        mode_text = "Dark Mode" if self.is_dark else "Light Mode"
        ToastNotification.show_info(f"Theme switched to {mode_text}", self)
