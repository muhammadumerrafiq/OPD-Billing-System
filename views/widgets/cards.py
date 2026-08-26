from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from views.widgets.svg_icon import SVGIconFactory

class MetricCard(QFrame):
    def __init__(self, title, value, icon_name, color="#0F6CBD", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon_name = icon_name
        self.color = color

        self.setup_ui()

    def setup_ui(self):
        # Set frame properties
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("MetricCard")
        
        # Glassmorphic border, background, and hover animations
        # In PyQt, QFrame stylesheet lets us apply gorgeous styles
        self.setStyleSheet(f"""
            QFrame#MetricCard {{
                background-color: rgba(255, 255, 255, 0.7); /* Translucent white background */
                border: 1px solid rgba(226, 232, 240, 0.8);
                border-radius: 12px;
            }}
            QFrame#MetricCard:hover {{
                border: 1px solid {self.color};
                background-color: rgba(255, 255, 255, 0.9);
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        # Main Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Text Section (Vertical)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(6)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Title Label
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Outfit", 10, QFont.Weight.Medium))
        self.title_label.setStyleSheet("color: #64748B;") # Cool Slate Muted
        text_layout.addWidget(self.title_label)

        # Value Label
        self.value_label = QLabel(str(self.value))
        self.value_label.setFont(QFont("Outfit", 20, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #1E293B;") # Slate Dark
        text_layout.addWidget(self.value_label)

        layout.addLayout(text_layout, 1)

        # Icon Container (Styled circle background)
        self.icon_container = QFrame()
        self.icon_container.setFixedSize(52, 52)
        # Convert hex code to RGBA for subtle transparent icon background
        rgba_color = self._hex_to_rgba(self.color, 0.12)
        self.icon_container.setStyleSheet(f"""
            QFrame {{
                background-color: {rgba_color};
                border-radius: 26px;
                border: none;
            }}
        """)
        
        icon_layout = QHBoxLayout(self.icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon_label = QLabel()
        pix = SVGIconFactory.get_pixmap(self.icon_name, color=self.color, size=(26, 26))
        self.icon_label.setPixmap(pix)
        icon_layout.addWidget(self.icon_label)

        layout.addWidget(self.icon_container)

        # Add drop shadow for depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 15)) # Ultra soft shadow
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def set_value(self, new_value):
        """Allows updating the metric value dynamically."""
        self.value = new_value
        self.value_label.setText(str(new_value))

    def update_theme(self, is_dark_mode):
        """Updates styling based on theme changes."""
        if is_dark_mode:
            self.setStyleSheet(f"""
                QFrame#MetricCard {{
                    background-color: rgba(30, 41, 59, 0.7); /* Translucent slate dark */
                    border: 1px solid rgba(51, 65, 85, 0.8);
                    border-radius: 12px;
                }}
                QFrame#MetricCard:hover {{
                    border: 1px solid {self.color};
                    background-color: rgba(30, 41, 59, 0.9);
                }}
                QLabel {{
                    background: transparent;
                    border: none;
                }}
            """)
            self.title_label.setStyleSheet("color: #94A3B8;") # Lighter Muted Slate
            self.value_label.setStyleSheet("color: #F8FAFC;") # White-ish slate
        else:
            self.setStyleSheet(f"""
                QFrame#MetricCard {{
                    background-color: rgba(255, 255, 255, 0.7); /* Translucent white background */
                    border: 1px solid rgba(226, 232, 240, 0.8);
                    border-radius: 12px;
                }}
                QFrame#MetricCard:hover {{
                    border: 1px solid {self.color};
                    background-color: rgba(255, 255, 255, 0.9);
                }}
                QLabel {{
                    background: transparent;
                    border: none;
                }}
            """)
            self.title_label.setStyleSheet("color: #64748B;") # Cool Slate Muted
            self.value_label.setStyleSheet("color: #1E293B;") # Slate Dark

    def _hex_to_rgba(self, hex_color, alpha):
        """Helper to convert #RRGGBB to rgba(r, g, b, a)."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
