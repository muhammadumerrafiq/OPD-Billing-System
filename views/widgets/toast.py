from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtGui import QColor, QFont
from views.widgets.svg_icon import SVGIconFactory

class ToastNotification(QWidget):
    def __init__(self, message, toast_type="success", parent=None, duration=3000):
        super().__init__(parent)
        self.message = message
        self.toast_type = toast_type.lower() # 'success', 'error', 'info'
        self.duration = duration

        # Configure window properties
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # UI Elements
        self.setup_ui()

        # Timer for dismissal
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fade_out)

    def setup_ui(self):
        # Container widget for styling
        self.container = QWidget(self)
        
        # Styles based on type
        border_color = "#10B981" # default success green
        icon_name = "check"
        if self.toast_type == "error":
            border_color = "#EF4444"
            icon_name = "delete"
        elif self.toast_type == "info":
            border_color = "#38BDF8"
            icon_name = "info"

        # Theme styling (Glassmorphism look with soft borders and gradients)
        self.container.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(30, 41, 59, 0.95); /* Deep slate translucent */
                border: 1.5px solid {border_color};
                border-radius: 8px;
            }}
        """)

        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        # Icon Label
        self.icon_label = QLabel()
        pix = SVGIconFactory.get_pixmap(icon_name, color=border_color, size=(20, 20))
        self.icon_label.setPixmap(pix)
        self.icon_label.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.icon_label)

        # Text Label
        self.text_label = QLabel(self.message)
        self.text_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.text_label.setStyleSheet("color: #F8FAFC; border: none; background: transparent;")
        self.text_label.setWordWrap(True)
        layout.addWidget(self.text_label)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        # Wrap in main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)

        self.adjustSize()

    def show_toast(self):
        # Position toast in top-right of parent or screen
        parent = self.parentWidget()
        if parent:
            parent_rect = parent.geometry()
            # Calculate top-right position
            pos = parent.mapToGlobal(QPoint(
                parent_rect.width() - self.width() - 25,
                25
            ))
        else:
            # Fallback to screen corner if no parent
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            pos = QPoint(
                screen.width() - self.width() - 30,
                50
            )

        self.move(pos)
        self.setWindowOpacity(0.0)
        self.show()

        # Fade in animation
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

        # Start timer for auto fadeout
        self.timer.start(self.duration)

    def fade_out(self):
        self.timer.stop()
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim.finished.connect(self.close)
        self.anim.start()

    @staticmethod
    def show_success(message, parent=None, duration=3500):
        toast = ToastNotification(message, "success", parent, duration)
        toast.show_toast()

    @staticmethod
    def show_error(message, parent=None, duration=4000):
        toast = ToastNotification(message, "error", parent, duration)
        toast.show_toast()

    @staticmethod
    def show_info(message, parent=None, duration=3500):
        toast = ToastNotification(message, "info", parent, duration)
        toast.show_toast()
