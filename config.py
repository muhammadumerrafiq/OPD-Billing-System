import os
import sys

class AppConfig:
    # Colors
    COLOR_PRIMARY = "#0F6CBD"      # Hospital Deep Blue
    COLOR_SECONDARY = "#38BDF8"    # Sky Blue
    COLOR_SUCCESS = "#10B981"      # Emerald Green
    COLOR_DANGER = "#EF4444"       # Rose Red
    
    # Light Mode Colors
    COLOR_LIGHT_BG = "#F8FAFC"      # Slate 50
    COLOR_LIGHT_CARD = "#FFFFFF"
    COLOR_LIGHT_TEXT = "#1E293B"    # Slate 800
    COLOR_LIGHT_MUTED = "#64748B"   # Slate 500
    COLOR_LIGHT_BORDER = "#E2E8F0"  # Slate 200

    # Dark Mode Colors
    COLOR_DARK_BG = "#0F172A"       # Slate 900
    COLOR_DARK_CARD = "#1E293B"     # Slate 800
    COLOR_DARK_TEXT = "#F8FAFC"     # Slate 50
    COLOR_DARK_MUTED = "#94A3B8"    # Slate 400
    COLOR_DARK_BORDER = "#334155"   # Slate 700

    # Font Families
    FONT_PRIMARY = "Outfit"
    FONT_SECONDARY = "Segoe UI"

    # CSS Stylesheets
    @classmethod
    def get_stylesheet(cls, is_dark=False):
        if is_dark:
            bg = cls.COLOR_DARK_BG
            card = cls.COLOR_DARK_CARD
            text = cls.COLOR_DARK_TEXT
            muted = cls.COLOR_DARK_MUTED
            border = cls.COLOR_DARK_BORDER
            input_bg = "rgba(15, 23, 42, 0.6)"
            hover_bg = "rgba(51, 65, 85, 0.4)"
            item_hover = "rgba(15, 23, 42, 0.4)"
        else:
            bg = cls.COLOR_LIGHT_BG
            card = cls.COLOR_LIGHT_CARD
            text = cls.COLOR_LIGHT_TEXT
            muted = cls.COLOR_LIGHT_MUTED
            border = cls.COLOR_LIGHT_BORDER
            input_bg = "#FFFFFF"
            hover_bg = "rgba(226, 232, 240, 0.4)"
            item_hover = "rgba(241, 245, 249, 0.8)"

        primary = cls.COLOR_PRIMARY
        secondary = cls.COLOR_SECONDARY
        success = cls.COLOR_SUCCESS
        danger = cls.COLOR_DANGER

        arrow_file = "down_arrow_dark.svg" if is_dark else "down_arrow_light.svg"
        if getattr(sys, 'frozen', False):
            arrow_path = os.path.join(sys._MEIPASS, "views", "widgets", arrow_file).replace("\\", "/")
        else:
            arrow_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "views", "widgets", arrow_file).replace("\\", "/")

        return f"""
            /* Global settings */
            QWidget {{
                color: {text};
                font-family: '{cls.FONT_SECONDARY}', 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }}
            
            QMainWindow {{
                background-color: {bg};
            }}

            /* Login Card & Content panels */
            QFrame#ContentPanel, QFrame#LoginCard {{
                background-color: {card};
                border: 1px solid {border};
                border-radius: 12px;
            }}

            /* Sidebar Frame */
            QFrame#SidebarFrame {{
                background-color: {card};
                border-right: 1px solid {border};
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }}

            /* Input Fields */
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {input_bg};
                border: 1.5px solid {border};
                border-radius: 8px;
                padding: 8px 12px;
                color: {text};
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 1.5px solid {primary};
            }}
            QLineEdit:disabled {{
                background-color: {hover_bg};
                color: {muted};
            }}

            /* Spinboxes */
            QSpinBox, QDoubleSpinBox {{
                background-color: {input_bg};
                border: 1.5px solid {border};
                border-radius: 6px;
                padding: 6px 10px;
                color: {text};
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 1.5px solid {primary};
            }}

            /* Dropdowns */
            QComboBox {{
                background-color: {input_bg};
                border: 1.5px solid {border};
                border-radius: 8px;
                padding: 8px 12px;
                color: {text};
            }}
            QComboBox:focus {{
                border: 1.5px solid {primary};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 0px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
            QComboBox::down-arrow {{
                image: url({arrow_path});
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {card};
                border: 1px solid {border};
                selection-background-color: {primary};
                selection-color: #FFFFFF;
                border-radius: 6px;
                padding: 4px;
            }}

            /* Standard Buttons */
            QPushButton {{
                background-color: {primary};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #0c5796;
            }}
            QPushButton:pressed {{
                background-color: #083c68;
            }}
            QPushButton:disabled {{
                background-color: {border};
                color: {muted};
            }}

            /* Outline Buttons */
            QPushButton#BtnOutline {{
                background-color: transparent;
                border: 1.5px solid {border};
                color: {text};
            }}
            QPushButton#BtnOutline:hover {{
                background-color: {hover_bg};
                border: 1.5px solid {primary};
            }}
            QPushButton#BtnOutline:pressed {{
                background-color: {border};
            }}

            /* Danger Buttons */
            QPushButton#BtnDanger {{
                background-color: {danger};
                color: #FFFFFF;
            }}
            QPushButton#BtnDanger:hover {{
                background-color: #dc2626;
            }}
            QPushButton#BtnDanger:pressed {{
                background-color: #991b1b;
            }}

            /* Success Buttons */
            QPushButton#BtnSuccess {{
                background-color: {success};
                color: #FFFFFF;
            }}
            QPushButton#BtnSuccess:hover {{
                background-color: #059669;
            }}
            QPushButton#BtnSuccess:pressed {{
                background-color: #065f46;
            }}

            /* Sidebar Navigation Buttons */
            QPushButton#SidebarBtn {{
                background-color: transparent;
                color: {muted};
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: 500;
                text-align: left;
            }}
            QPushButton#SidebarBtn:hover {{
                background-color: {hover_bg};
                color: {text};
            }}
            QPushButton#SidebarBtn:checked {{
                background-color: rgba(15, 108, 189, 0.1);
                color: {primary};
                font-weight: bold;
                border-left: 4px solid {primary};
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }}

            /* Headers and Labels */
            QLabel#TitleLabel {{
                font-family: '{cls.FONT_PRIMARY}', 'Segoe UI', sans-serif;
                font-size: 20px;
                font-weight: bold;
                color: {primary};
            }}
            QLabel#SubTitleLabel {{
                color: {muted};
                font-size: 12px;
            }}
            QLabel#LoginTitle {{
                font-family: '{cls.FONT_PRIMARY}', 'Segoe UI', sans-serif;
                font-size: 24px;
                font-weight: bold;
                color: {primary};
            }}

            /* Table Styling */
            QTableWidget, QTableView {{
                background-color: {card};
                border: 1px solid {border};
                border-radius: 8px;
                gridline-color: {border};
                selection-background-color: rgba(15, 108, 189, 0.15);
                selection-color: {text};
            }}
            QHeaderView::section {{
                background-color: {primary};
                color: #FFFFFF;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 0.15);
            }}
            QHeaderView::section:horizontal {{
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
            }}
            QTableWidget::item, QTableView::item {{
                padding: 6px;
                border-bottom: 1px solid {border};
            }}
            QTableWidget::item:hover, QTableView::item:hover {{
                background-color: {item_hover};
            }}

            /* Tab Widget */
            QTabWidget::pane {{
                border: 1px solid {border};
                background: {card};
                border-radius: 8px;
                top: -1px;
            }}
            QTabBar::tab {{
                background: {hover_bg};
                border: 1px solid {border};
                border-bottom-color: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 4px;
                color: {muted};
            }}
            QTabBar::tab:selected, QTabBar::tab:hover {{
                background: {card};
                border-bottom-color: {card};
                color: {primary};
                font-weight: bold;
            }}

            /* Scrollbars */
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {muted};
                min-height: 20px;
                border-radius: 4px;
                opacity: 0.6;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {primary};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: transparent;
                height: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {muted};
                min-width: 20px;
                border-radius: 4px;
                opacity: 0.6;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
                width: 0px;
            }}
        """
