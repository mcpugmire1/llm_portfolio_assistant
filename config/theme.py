"""
Theme Configuration - MattGPT Design System

Single source of truth for colors, typography, and spacing.
Ensures consistency across all UI components.
"""

# Color Palette
COLORS = {
    # Primary Brand Colors
    "primary_purple": "#8B5CF6",
    "primary_purple_alt": "#7c3aed",
    "secondary_purple": "#764ba2",
    "purple_gradient_start": "#667eea",
    "purple_gradient_end": "#764ba2",
    # Navigation & Dark Elements
    "dark_navy": "#2c3e50",
    "dark_navy_hover": "#34495e",
    "dark_slate": "#334155",
    # Backgrounds
    "white": "#ffffff",
    "light_gray_bg": "#f8f9fa",
    "page_bg": "#f5f5f5",
    # Borders & Dividers
    "border_gray": "#e5e5e5",
    "border_gray_alt": "#e0e0e0",
    # Text Colors
    "text_dark": "#1a1a1a",
    "text_dark_alt": "#333333",
    "text_medium": "#555555",
    "text_light": "#6b7280",
    "text_gray": "#7f8c8d",
    "text_muted": "#888888",
}

# Typography
TYPOGRAPHY = {
    "hero_title": "48px",
    "page_title": "32px",
    "section_title": "24px",
    "card_title": "18px",
    "body": "16px",
    "small": "14px",
    "tiny": "13px",
    "weight_normal": "400",
    "weight_medium": "500",
    "weight_semibold": "600",
    "weight_bold": "700",
}

# Spacing
SPACING = {
    "card_padding": "24px",
    "section_padding": "40px",
    "footer_padding": "80px 40px",
    "cta_padding": "48px 32px",
    "button_padding": "15px 32px",
    "nav_padding": "16px 40px",
}

# Border Radius
BORDER_RADIUS = {
    "small": "6px",
    "medium": "8px",
    "large": "12px",
    "pill": "20px",
}

# Shadows
SHADOWS = {
    "subtle": "0 1px 3px rgba(0,0,0,0.08)",
    "card": "0 2px 8px rgba(0, 0, 0, 0.15)",
    "card_hover": "0 4px 12px rgba(124, 58, 237, 0.15)",
    "button": "0 4px 12px rgba(139, 92, 246, 0.3)",
}

# CSS Gradients
GRADIENTS = {
    "purple_hero": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
}
