"""
Enable/Disable Mobile Responsive CSS

This script safely integrates mobile_overrides.py into global_styles.py
without breaking existing functionality.

Usage:
    python scripts/enable_mobile_css.py --enable    # Turn on mobile CSS
    python scripts/enable_mobile_css.py --disable   # Turn off mobile CSS
    python scripts/enable_mobile_css.py --status    # Check current status
"""

import sys
from pathlib import Path


def get_global_styles_path() -> Path:
    """Get path to global_styles.py"""
    return Path(__file__).parent.parent / "ui" / "styles" / "global_styles.py"


def is_mobile_css_enabled() -> bool:
    """Check if mobile CSS is currently enabled"""
    styles_path = get_global_styles_path()
    content = styles_path.read_text()
    return "from ui.styles.mobile_overrides import get_mobile_css" in content


def enable_mobile_css() -> None:
    """Add mobile CSS import to global_styles.py"""
    styles_path = get_global_styles_path()
    content = styles_path.read_text()

    if "from ui.styles.mobile_overrides import get_mobile_css" in content:
        print("✅ Mobile CSS is already enabled")
        return

    # Find the end of apply_global_styles() function
    lines = content.split("\n")
    modified_lines = []
    inside_function = False
    injection_done = False

    for i, line in enumerate(lines):
        modified_lines.append(line)

        # Detect function start
        if "def apply_global_styles():" in line:
            inside_function = True

        # Inject before the closing of the function
        if (
            inside_function
            and not injection_done
            and i + 1 < len(lines)
            and (
                lines[i + 1].strip() == ""
                or not lines[i + 1].startswith("    ")
                or "def " in lines[i + 1]
            )
            and "st.markdown" in line
        ):
            modified_lines.append("")
            modified_lines.append("    # Mobile responsive CSS overrides")
            modified_lines.append(
                "    from ui.styles.mobile_overrides import get_mobile_css"
            )
            modified_lines.append(
                "    st.markdown(get_mobile_css(), unsafe_allow_html=True)"
            )
            injection_done = True
            inside_function = False

    # Write back
    styles_path.write_text("\n".join(modified_lines))
    print("✅ Mobile CSS enabled successfully!")
    print("   Run your Streamlit app to see responsive behavior at <768px")


def disable_mobile_css() -> None:
    """Remove mobile CSS import from global_styles.py"""
    styles_path = get_global_styles_path()
    content = styles_path.read_text()

    if "from ui.styles.mobile_overrides import get_mobile_css" not in content:
        print("✅ Mobile CSS is already disabled")
        return

    # Remove the mobile CSS lines
    lines = content.split("\n")
    filtered_lines = []
    skip_next = 0

    for line in lines:
        if skip_next > 0:
            skip_next -= 1
            continue

        if "# Mobile responsive CSS overrides" in line:
            skip_next = 2  # Skip the next 2 lines (import and markdown call)
            continue

        filtered_lines.append(line)

    # Write back
    styles_path.write_text("\n".join(filtered_lines))
    print("✅ Mobile CSS disabled successfully!")
    print("   App will return to desktop-only mode")


def show_status() -> None:
    """Show current mobile CSS status"""
    enabled = is_mobile_css_enabled()
    status = "ENABLED ✅" if enabled else "DISABLED ❌"
    print(f"Mobile CSS Status: {status}")

    if enabled:
        print("\nTo disable: python scripts/enable_mobile_css.py --disable")
    else:
        print("\nTo enable: python scripts/enable_mobile_css.py --enable")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "--enable":
        enable_mobile_css()
    elif command == "--disable":
        disable_mobile_css()
    elif command == "--status":
        show_status()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
