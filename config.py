"""
DigiCal Configuration Settings
"""
import os

# Application Settings
APP_NAME = "DigiCal Business Calculator"
VERSION = "1.0.0"

# Display Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 480
DISPLAY_FONT = ("Arial", 24, "bold")
BUTTON_FONT = ("Arial", 14)
LABEL_FONT = ("Arial", 12)

# Color Scheme
BG_COLOR = "#2C3E50"
DISPLAY_BG = "#34495E"
DISPLAY_FG = "#ECF0F1"
BUTTON_BG = "#3498DB"
BUTTON_FG = "#FFFFFF"
BUTTON_ACTIVE = "#2980B9"
OPERATOR_BG = "#E67E22"
EQUALS_BG = "#27AE60"
MODE_BG = "#9B59B6"

# Database Settings
DB_PATH = os.path.join(os.path.dirname(__file__), "digical.db")

# Currency Settings
CURRENCY_SYMBOL = "₹"

# Payment Methods
PAYMENT_METHODS = ["UPI", "Cash"]

# Default Categories
DEFAULT_SALES_CATEGORIES = [
    "Product Sales",
    "Service Sales",
    "Consulting",
    "Other Income"
]

DEFAULT_EXPENSE_CATEGORIES = [
    "Rent",
    "Utilities",
    "Supplies",
    "Salaries",
    "Marketing",
    "Transportation",
    "Other Expenses"
]

# History Settings
MAX_HISTORY_ITEMS = 100

# Graph settings
GRAPH_FIGSIZE = (8, 5)
GRAPH_DPI = 80

# Web Portal settings
WEB_HOST = '0.0.0.0'  # Listen on all network interfaces (allows WiFi access)
WEB_PORT = 8128  # Web server port
API_REFRESH_INTERVAL = 30  # Auto-refresh interval in seconds


