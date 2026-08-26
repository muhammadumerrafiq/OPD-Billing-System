import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QColor

class ChartCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3.5, dpi=100, is_dark=False):
        # Create matplotlib Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.is_dark = is_dark
        
        # Configure canvas
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Style chart figure
        self.apply_theme_styling()

    def apply_theme_styling(self):
        """Styles the chart canvas based on theme settings."""
        if self.is_dark:
            # Dark slate color palette matching the application UI
            bg_color = '#1E293B'      # Slate 800
            text_color = '#F8FAFC'    # Slate 50
            grid_color = '#334155'    # Slate 700
        else:
            # Light mode theme colors
            bg_color = '#FFFFFF'
            text_color = '#1E293B'    # Slate 800
            grid_color = '#F1F5F9'    # Slate 100

        self.fig.patch.set_facecolor(bg_color)
        self.axes.set_facecolor(bg_color)
        
        # Set colors for labels, titles, ticks
        self.axes.tick_params(colors=text_color, labelsize=9)
        self.axes.xaxis.label.set_color(text_color)
        self.axes.yaxis.label.set_color(text_color)
        self.axes.title.set_color(text_color)
        
        # Grid settings
        self.axes.grid(True, color=grid_color, linestyle='--', linewidth=0.5)
        
        # Border box spines
        for spine in self.axes.spines.values():
            spine.set_color(grid_color)
            spine.set_linewidth(1.0)


class RevenueChartCanvas(ChartCanvas):
    def update_chart(self, date_list, revenue_list):
        """Plots a sleek area/line chart showing daily revenue."""
        self.axes.clear()
        self.apply_theme_styling()
        
        primary_color = "#0F6CBD"  # Core Theme Blue
        secondary_color = "#38BDF8"
        
        # Check if data exists
        if not date_list:
            self.axes.text(0.5, 0.5, "No Revenue Data Available", 
                           ha='center', va='center', fontsize=12,
                           color='#94A3B8')
            self.draw()
            return

        # Shorten dates to MM-DD for label fit
        x_labels = []
        for d in date_list:
            try:
                parts = d.split('-')
                x_labels.append(f"{parts[1]}-{parts[2]}")
            except:
                x_labels.append(d)

        # Plot line
        self.axes.plot(x_labels, revenue_list, color=primary_color, 
                       marker='o', markersize=4, linewidth=2.5, 
                       label="Revenue")
        
        # Area fill under the line for a premium modern gradient-like effect
        self.axes.fill_between(x_labels, revenue_list, color=primary_color, 
                               alpha=0.15)
        
        # Title & Ticks format
        self.axes.set_title("Revenue (Last 7 Days)", fontsize=11, fontweight='bold', pad=10)
        self.axes.set_ylabel("Revenue (Rs)", fontsize=9)
        self.axes.tick_params(axis='x', rotation=15)
        
        # Tight layout adjustment
        self.fig.tight_layout()
        self.draw()


class RegistrationChartCanvas(ChartCanvas):
    def update_chart(self, date_list, counts_list):
        """Plots a beautiful bar chart representing registrations."""
        self.axes.clear()
        self.apply_theme_styling()
        
        accent_color = "#10B981"  # Success Teal/Green
        
        if not date_list:
            self.axes.text(0.5, 0.5, "No Patient Registrations", 
                           ha='center', va='center', fontsize=12,
                           color='#94A3B8')
            self.draw()
            return

        x_labels = []
        for d in date_list:
            try:
                parts = d.split('-')
                x_labels.append(f"{parts[1]}-{parts[2]}")
            except:
                x_labels.append(d)

        # Plot vertical bars
        bars = self.axes.bar(x_labels, counts_list, color=accent_color, 
                             width=0.4, edgecolor='none', alpha=0.85)
        
        # Title & Ticks format
        self.axes.set_title("New Patients Registered (Last 7 Days)", fontsize=11, fontweight='bold', pad=10)
        self.axes.set_ylabel("Patients Count", fontsize=9)
        self.axes.tick_params(axis='x', rotation=15)

        # Force Y axis to display integer ticks only
        max_y = max(counts_list) if counts_list else 1
        self.axes.set_ylim(0, max_y + 1)
        
        # Tight layout adjustment
        self.fig.tight_layout()
        self.draw()


class QtChartWidget(QWidget):
    """Container widget wrapping the matplotlib canvas."""
    def __init__(self, chart_type="revenue", parent=None, is_dark=False):
        super().__init__(parent)
        self.chart_type = chart_type
        self.is_dark = is_dark
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if self.chart_type == "revenue":
            self.canvas = RevenueChartCanvas(self, is_dark=is_dark)
        else:
            self.canvas = RegistrationChartCanvas(self, is_dark=is_dark)
            
        layout.addWidget(self.canvas)

    def update_data(self, date_list, values_list):
        self.canvas.update_chart(date_list, values_list)

    def set_theme(self, is_dark):
        self.canvas.is_dark = is_dark
        self.canvas.apply_theme_styling()
        self.canvas.draw()
