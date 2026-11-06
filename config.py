"""
Little Ledger - Configuration & Design System Constants
Centralized settings, botanical color tokens, typography styles, and financial formatting helpers.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

MODELS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Database Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "little_ledger")
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "demo_user")
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "INR")

# Botanical Design Palette Tokens (From Design Specification)
PALETTE = {
    "bg_main": "#FAF8F3",         # Warm ivory paper tone
    "surface": "#FFFFFF",         # Pure card white
    "surface_alt": "#F5F2EB",     # Subtle paper tint
    "primary_green": "#657B68",   # Sage green accent
    "primary_dark": "#435646",    # Deep forest green
    "dusty_peach": "#D9B8A7",     # Soft terra cotta / peach
    "lavender": "#D9D1EB",        # Botanical lavender
    "butter_yellow": "#F0E3A8",   # Soft mustard butter
    "powder_blue": "#C9DCE8",     # Muted duck-egg blue
    "blush_pink": "#E7C2C0",      # Delicate rose blush
    "text_main": "#292D29",       # Deep charcoal for headings/body
    "text_muted": "#77796F",      # Muted slate secondary text
    "text_light": "#A0A299",      # Tertiary caption text
    "border": "#E8E4DA",          # Delicate paper hairline border
    "border_subtle": "#F0ECE2",   # Ultra-soft separator
    "success": "#53765C",         # Botanical forest green
    "warning": "#A46B35",         # Warm ochre warning
    "error": "#B65E58",           # Terracotta crimson alert
    "card_shadow": "0 2px 12px rgba(41, 45, 41, 0.04)",
    "card_shadow_hover": "0 8px 24px rgba(41, 45, 41, 0.08)",
}

# Standard Categories and Default Allocations
CATEGORIES = [
    "Food & Dining",
    "Housing & Utilities",
    "Shopping & Home",
    "Transport & Mobility",
    "Entertainment & Culture",
    "Health & Wellness",
    "Books & Learning",
    "Discretionary Reserve",
]

# Category Display Metadata
CATEGORY_META = {
    "Food & Dining": {"color": PALETTE["primary_green"], "icon": "🍽️", "nature": "Needs"},
    "Housing & Utilities": {"color": PALETTE["powder_blue"], "icon": "🏡", "nature": "Needs"},
    "Shopping & Home": {"color": PALETTE["dusty_peach"], "icon": "🛍️", "nature": "Wants"},
    "Transport & Mobility": {"color": PALETTE["lavender"], "icon": "🚆", "nature": "Needs"},
    "Entertainment & Culture": {"color": PALETTE["blush_pink"], "icon": "🎭", "nature": "Wants"},
    "Health & Wellness": {"color": "#88B795", "icon": "🌿", "nature": "Needs"},
    "Books & Learning": {"color": PALETTE["butter_yellow"], "icon": "📚", "nature": "Wants"},
    "Discretionary Reserve": {"color": "#9CB5A0", "icon": "🛡️", "nature": "Buffer"},
}

# Payment Rails / Channels
PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "NetBanking",
    "Auto-Debit",
    "Cash",
]

def format_inr(amount: float, show_symbol: bool = True, decimals: int = 2) -> str:
    """
    Format numerical amounts according to Indian Numbering System (Lakhs & Crores).
    E.g., 142890.00 -> ₹1,42,890.00
    """
    if amount is None:
        return "₹0.00" if show_symbol else "0.00"
    
    is_negative = amount < 0
    amount = abs(amount)
    
    # Split into integer and decimal portions
    formatted_dec = f"{amount:.{decimals}f}".split(".")
    dec_part = f".{formatted_dec[1]}" if len(formatted_dec) > 1 and decimals > 0 else ""
    int_str = formatted_dec[0]
    
    if len(int_str) <= 3:
        formatted_int = int_str
    else:
        last_three = int_str[-3:]
        remaining = int_str[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted_int = ",".join(groups) + "," + last_three
        
    symbol = "₹" if show_symbol else ""
    sign = "-" if is_negative else ""
    return f"{sign}{symbol}{formatted_int}{dec_part}"

# Custom CSS for Streamlit
CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,500;9..144,600&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global Reset & Typography */
html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: {PALETTE["text_main"]};
    background-color: {PALETTE["bg_main"]};
}}

h1, h2, h3, .editorial-heading {{
    font-family: 'Fraunces', 'DM Serif Display', Georgia, serif !important;
    font-weight: 400;
    letter-spacing: -0.02em;
    color: {PALETTE["text_main"]};
}}

.tabular-num {{
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.01em;
}}

/* Top Navigation Bar */
.ll-navbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 24px;
    background-color: {PALETTE["surface"]};
    border-bottom: 1px solid {PALETTE["border"]};
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: {PALETTE["card_shadow"]};
}}

.ll-brand {{
    font-family: 'Fraunces', serif;
    font-size: 22px;
    font-weight: 500;
    color: {PALETTE["primary_dark"]};
    letter-spacing: -0.01em;
    display: flex;
    align-items: baseline;
    gap: 8px;
}}

.ll-brand-tag {{
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {PALETTE["text_muted"]};
    background: {PALETTE["surface_alt"]};
    padding: 3px 8px;
    border-radius: 4px;
    border: 1px solid {PALETTE["border_subtle"]};
}}

/* Editorial Card */
.ll-card {{
    background: {PALETTE["surface"]};
    border: 1px solid {PALETTE["border"]};
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: {PALETTE["card_shadow"]};
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}

.ll-card:hover {{
    box-shadow: {PALETTE["card_shadow_hover"]};
}}

.ll-card-header {{
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {PALETTE["text_muted"]};
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.ll-metric-value {{
    font-family: 'Fraunces', serif;
    font-size: 32px;
    font-weight: 500;
    color: {PALETTE["text_main"]};
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin: 4px 0 8px 0;
}}

.ll-metric-subtitle {{
    font-size: 13px;
    color: {PALETTE["text_muted"]};
    display: flex;
    align-items: center;
    gap: 6px;
}}

/* Pill Badges */
.ll-badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 3px 8px;
    border-radius: 20px;
}}

.ll-badge-green {{
    background-color: #EBF3ED;
    color: {PALETTE["success"]};
    border: 1px solid #D1E5D5;
}}

.ll-badge-amber {{
    background-color: #FDF6EC;
    color: {PALETTE["warning"]};
    border: 1px solid #F5E2C4;
}}

.ll-badge-red {{
    background-color: #FDF0EE;
    color: {PALETTE["error"]};
    border: 1px solid #F5D0CC;
}}

.ll-badge-neutral {{
    background-color: {PALETTE["surface_alt"]};
    color: {PALETTE["text_muted"]};
    border: 1px solid {PALETTE["border"]};
}}

/* Table Styling */
.ll-table {{
    width: 100% !important;
    border-collapse: collapse !important;
    font-size: 13.5px !important;
    table-layout: fixed !important;
}}

.ll-table th {{
    font-family: 'Inter', sans-serif !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: {PALETTE["text_muted"]} !important;
    background: {PALETTE["surface_alt"]} !important;
    padding: 12px 14px !important;
    border-bottom: 1px solid {PALETTE["border"]} !important;
    text-align: left !important;
    vertical-align: middle !important;
}}

.ll-table td {{
    padding: 12px 14px !important;
    border-bottom: 1px solid {PALETTE["border_subtle"]} !important;
    color: {PALETTE["text_main"]} !important;
    vertical-align: middle !important;
    word-break: break-word !important;
}}

.ll-table tr:hover td {{
    background-color: #FAF8F5 !important;
}}

.ll-table tr:last-child td {{
    border-bottom: none !important;
}}

/* Completely hide the left sidebar and its toggles */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"],
.stSidebar,
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"] {{
    display: none !important;
    width: 0px !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}}

/* Ensure clean centered full-width layout */
.main .block-container {{
    max-width: 1360px !important;
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}}

/* Segmented Control Pill Container */
div[data-testid="stSegmentedControl"] {{
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
}}

div[data-testid="stButtonGroup"] {{
    background-color: #F4F1EA !important;
    border: 1px solid #E5E0D4 !important;
    border-radius: 30px !important;
    padding: 3px !important;
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 2px !important;
    width: fit-content !important;
    margin-left: auto !important;
    margin-right: auto !important;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.03) !important;
}}

div[data-testid="stButtonGroup"] button {{
    border-radius: 24px !important;
    border: none !important;
    background-color: transparent !important;
    color: #65685F !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    padding: 5px 12px !important;
    margin: 0 !important;
    transition: all 0.16s ease !important;
    white-space: nowrap !important;
    flex-shrink: 0 !important;
    box-shadow: none !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 5px !important;
    line-height: 1 !important;
}}

div[data-testid="stButtonGroup"] button p,
div[data-testid="stButtonGroup"] button div {{
    margin: 0 !important;
    padding: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 4px !important;
    font-size: 12.5px !important;
    white-space: nowrap !important;
}}

div[data-testid="stButtonGroup"] button:hover {{
    color: #292D29 !important;
    background-color: rgba(255, 255, 255, 0.6) !important;
}}

div[data-testid="stButtonGroup"] button[data-testid="stBaseButton-segmented_controlActive"],
div[data-testid="stButtonGroup"] button[aria-checked="true"],
div[data-testid="stButtonGroup"] button[aria-selected="true"] {{
    background-color: #FFFFFF !important;
    color: #292D29 !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 6px rgba(41, 45, 41, 0.08) !important;
}}

/* User avatar button styling */
div.st-key-nav_btn_avatar button {{
    height: 38px !important;
    min-height: 38px !important;
    max-height: 38px !important;
    min-width: 52px !important;
    border-radius: 8px !important;
    background: #FAF8F3 !important;
    border: 1px solid #E5E0D4 !important;
    color: #555A52 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    padding: 0 10px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    white-space: nowrap !important;
    box-shadow: none !important;
}}

div.st-key-nav_btn_avatar button:hover {{
    background: #F0ECE2 !important;
    border-color: #555A52 !important;
    color: #292D29 !important;
}}

div.st-key-nav_btn_avatar button p,
div.st-key-nav_btn_avatar button div {{
    white-space: nowrap !important;
    word-break: keep-all !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
}}

/* Dialog Modal Width and Spacing */
div[data-testid="stDialog"] div[role="dialog"] {{
    max-width: 820px !important;
    width: 820px !important;
    border-radius: 16px !important;
    border: 1px solid #E5E0D4 !important;
    box-shadow: 0 20px 60px rgba(41, 45, 41, 0.18) !important;
}}

/* Hide deploy button and extra clutter */
.stDeployButton {{display:none !important;}}
#MainMenu {{visibility: hidden !important;}}
footer {{visibility: hidden !important;}}
</style>
"""
