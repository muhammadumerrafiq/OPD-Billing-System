from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPixmap
from config import AppConfig
from views.widgets.svg_icon import SVGIconFactory

class LoginView(QWidget):
    # Signal emitted when login credentials are submitted
    login_submitted = pyqtSignal(str, str)

    def __init__(self, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark_mode
        self.setup_ui()

    def setup_ui(self):
        # Set up a beautiful gradient background or subtle coloring
        self.setObjectName("LoginView")
        self.update_background()

        # Layout to center the login card
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login Card (Frame)
        self.card = QFrame()
        self.card.setObjectName("LoginCard")
        self.card.setFixedSize(380, 480)
        
        # Internal card layout
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(35, 40, 35, 40)
        card_layout.setSpacing(15)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Logo placeholder (Beautifully styled medical cross SVG)
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_logo()
        card_layout.addWidget(self.logo_label)

        # Hospital Name & Title
        self.title_label = QLabel("Bismel Medical Center")
        self.title_label.setObjectName("LoginTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.subtitle_label = QLabel("OPD Billing Management System")
        self.subtitle_label.setStyleSheet("color: #64748B; font-size: 13px; font-weight: 500;")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card_layout.addWidget(self.title_label)
        card_layout.addWidget(self.subtitle_label)
        card_layout.addSpacing(10)

        # Username Input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(42)
        self.username_input.setFont(QFont("Segoe UI", 10))
        card_layout.addWidget(self.username_input)

        # Password Input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(42)
        self.password_input.setFont(QFont("Segoe UI", 10))
        # Support Enter key trigger
        self.password_input.returnPressed.connect(self.on_login_click)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(10)

        # Login Button
        self.login_btn = QPushButton("Access System")
        self.login_btn.setMinimumHeight(42)
        self.login_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.on_login_click)
        card_layout.addWidget(self.login_btn)

        # Add drop shadow to the login card
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(shadow)

        main_layout.addWidget(self.card)

        # Load styling
        self.apply_theme_styling()

    def update_background(self):
        if self.is_dark:
            # Dark Mode background style
            self.setStyleSheet(f"""
                QWidget#LoginView {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #0F172A, stop:1 #1E293B);
                }}
            """)
        else:
            # Light Mode background style
            self.setStyleSheet(f"""
                QWidget#LoginView {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #F1F5F9, stop:1 #E2E8F0);
                }}
            """)

    def update_logo(self):
        import os
        import sys
        if getattr(sys, 'frozen', False):
            logo_path = os.path.join(sys._MEIPASS, "logo.jpeg")
        else:
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logo_path = os.path.join(project_dir, "logo.jpeg")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(110, 110, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pix)
        else:
            # Green cross for light mode, light blue cross for dark mode
            color = "#10B981" if not self.is_dark else "#38BDF8"
            pix = SVGIconFactory.get_pixmap("doctors", color=color, size=(64, 64))
            self.logo_label.setPixmap(pix)

    def apply_theme_styling(self):
        # Set stylesheet from AppConfig
        self.card.setStyleSheet(AppConfig.get_stylesheet(self.is_dark))
        self.update_background()
        self.update_logo()
        
        # Subtitle styling based on mode
        if self.is_dark:
            self.subtitle_label.setStyleSheet("color: #94A3B8; font-size: 13px; font-weight: 500;")
        else:
            self.subtitle_label.setStyleSheet("color: #64748B; font-size: 13px; font-weight: 500;")

    def on_login_click(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if username and password:
            self.login_submitted.emit(username, password)

    def clear_inputs(self):
        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setFocus()

    def set_theme(self, is_dark_mode):
        self.is_dark = is_dark_mode
        self.apply_theme_styling()
