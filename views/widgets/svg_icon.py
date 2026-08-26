from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, QSize
from utils.logger import logger

class SVGIconFactory:
    # A registry of crisp, modern SVG designs
    _svg_data = {
        "dashboard": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="7" height="9"></rect>
                <rect x="14" y="3" width="7" height="5"></rect>
                <rect x="14" y="12" width="7" height="9"></rect>
                <rect x="3" y="16" width="7" height="5"></rect>
            </svg>
        """,
        "patients_reg": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="8.5" cy="7" r="4"></circle>
                <line x1="20" y1="8" x2="20" y2="14"></line>
                <line x1="17" y1="11" x2="23" y2="11"></line>
            </svg>
        """,
        "patients_rec": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="8.5" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
        """,
        "doctors": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 12h-2v3a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-3H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2z"></path>
                <path d="M12 2v2"></path>
                <path d="M12 17v5"></path>
                <path d="M8 22h8"></path>
            </svg>
        """,
        "procedures": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
        """,
        "lab_tests": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4.5 16.5c-1.5 1.25-2.5 3-2.5 4.5h20c0-1.5-1-3.25-2.5-4.5L14 4h-4L4.5 16.5z"></path>
                <line x1="8" y1="2" x2="16" y2="2"></line>
                <line x1="9" y1="11" x2="15" y2="11"></line>
            </svg>
        """,
        "billing": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="1" x2="12" y2="23"></line>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
        """,
        "history": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
                <path d="M12 2a10 10 0 1 0 10 10h-2"></path>
            </svg>
        """,
        "reports": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
        """,
        "settings": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
        """,
        "sun": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
        """,
        "moon": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
        """,
        "search": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
        """,
        "edit": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
        """,
        "delete": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                <line x1="10" y1="11" x2="10" y2="17"></line>
                <line x1="14" y1="11" x2="14" y2="17"></line>
            </svg>
        """,
        "add": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
        """,
        "save": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                <polyline points="17 21 17 13 7 13 7 21"></polyline>
                <polyline points="7 3 7 8 15 8"></polyline>
            </svg>
        """,
        "print": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 6 2 18 2 18 9"></polyline>
                <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
                <rect x="6" y="14" width="12" height="8"></rect>
            </svg>
        """,
        "pdf": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <path d="M10 13a2.5 2.5 0 0 0-2.5 2.5v2"></path>
                <path d="M14 13a2.5 2.5 0 0 0-2.5 2.5v2"></path>
                <circle cx="12" cy="15" r="1"></circle>
            </svg>
        """,
        "logout": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
        """,
        "info": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
        """,
        "check": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
        """,
        "refresh": """
            <svg viewBox="0 0 24 24" fill="none" stroke="ATTR_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path>
            </svg>
        """
    }

    @classmethod
    def get_icon(cls, name, color="#0F6CBD", size=(24, 24)):
        """Generates a QIcon from the SVG registry using custom color and size."""
        svg_xml = cls._svg_data.get(name)
        if not svg_xml:
            logger.warning(f"SVG icon '{name}' not found. Returning empty QIcon.")
            return QIcon()

        # Inject color attribute
        colored_svg = svg_xml.replace("ATTR_COLOR", color)
        
        # Parse XML
        bytes_data = QByteArray(colored_svg.encode('utf-8'))
        
        try:
            renderer = QSvgRenderer(bytes_data)
            
            # Create a Pixmap to paint onto
            pixmap = QPixmap(size[0], size[1])
            from PyQt6.QtGui import QColor
            pixmap.fill(QColor(0, 0, 0, 0)) # Fully transparent QColor

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            return QIcon(pixmap)
        except Exception as e:
            logger.error(f"Failed to render SVG icon '{name}': {str(e)}")
            return QIcon()

    @classmethod
    def get_pixmap(cls, name, color="#0F6CBD", size=(32, 32)):
        """Generates a QPixmap from the SVG registry."""
        svg_xml = cls._svg_data.get(name)
        if not svg_xml:
            return QPixmap()
        colored_svg = svg_xml.replace("ATTR_COLOR", color)
        bytes_data = QByteArray(colored_svg.encode('utf-8'))
        try:
            renderer = QSvgRenderer(bytes_data)
            pixmap = QPixmap(size[0], size[1])
            from PyQt6.QtGui import QColor
            pixmap.fill(QColor(0, 0, 0, 0))
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            return pixmap
        except Exception as e:
            logger.error(f"Failed to render SVG pixmap '{name}': {str(e)}")
            return QPixmap()
