"""
Regression test script for Explore Stories UI
Tests key elements to ensure they render correctly
"""

import subprocess
import sys
import time


def run_streamlit_test():
    """Launch Streamlit and check if it starts without errors"""
    print("🔍 Starting Streamlit UI regression test...")

    try:
        # Start Streamlit in the background
        proc = subprocess.Popen(
            ["streamlit", "run", "app.py", "--server.headless", "true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for startup
        time.sleep(5)

        # Check if process is still running
        if proc.poll() is None:
            print("✅ Streamlit app started successfully")
            proc.terminate()
            return True
        else:
            stdout, stderr = proc.communicate()
            print("❌ Streamlit failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False

    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        return False


def check_code_patterns():
    """Check for known problematic patterns in app.py"""
    print("\n🔍 Checking code patterns...")

    issues = []

    with open("app.py", "r") as f:
        content = f.read()
        lines = content.split("\n")

    # Check 1: Results summary uses columns
    if 'col1, col2, col3, col4 = st.columns' in content:
        print("✅ Results summary uses column layout")
    else:
        issues.append("Results summary not using proper column layout")

    # Check 2: AgGrid uses flex or width configuration
    if 'gob.configure_column("Title"' in content:
        print("✅ AgGrid column configuration found")
    else:
        issues.append("AgGrid column configuration missing")

    # Check 3: No excessive negative margins
    negative_margin_count = content.count("margin-top: -")
    if negative_margin_count > 3:
        issues.append(f"Too many negative margins ({negative_margin_count}) - may cause alignment issues")
    else:
        print(f"✅ Negative margin usage acceptable ({negative_margin_count})")

    # Check 4: Selectbox has options
    if 'options=[10, 20, 50]' in content:
        print("✅ Selectbox has correct options")
    else:
        issues.append("Selectbox options may be incorrect")

    # Check 5: Pagination buttons exist
    if '"First"' in content and '"Prev"' in content and '"Next"' in content and '"Last"' in content:
        print("✅ Pagination buttons configured")
    else:
        issues.append("Pagination buttons may be missing or misconfigured")

    # Check 6: AgGrid has height parameter for scrolling
    if 'height=' in content and 'AgGrid(' in content:
        print("✅ AgGrid height parameter configured (enables scrolling)")
    else:
        issues.append("AgGrid height parameter missing - table may not scroll")

    # Check 7: Column proportions look reasonable
    if 'st.columns([2.' in content:
        print("✅ Column layout proportions found")
    else:
        issues.append("Column layout may have incorrect proportions")

    return issues


def main():
    print("=" * 60)
    print("Explore Stories UI Regression Test")
    print("=" * 60)
    print("\n⚠️  NOTE: This test only checks code patterns and startup.")
    print("    It does NOT verify visual rendering, alignment, or scrolling.")
    print("    Use UI_CHECKLIST.md for manual visual verification.\n")

    # Check code patterns
    code_issues = check_code_patterns()

    if code_issues:
        print("\n❌ Code issues found:")
        for issue in code_issues:
            print(f"  - {issue}")
    else:
        print("\n✅ All code pattern checks passed")

    # Run Streamlit test
    streamlit_ok = run_streamlit_test()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Code Checks: {'✅ PASS' if not code_issues else '❌ FAIL'}")
    print(f"Streamlit Launch: {'✅ PASS' if streamlit_ok else '❌ FAIL'}")

    print("\n⚠️  LIMITATIONS:")
    print("  - Does not test visual rendering")
    print("  - Does not test element alignment")
    print("  - Does not test scrolling behavior")
    print("  - Does not test dropdown width/height")
    print("  → Manual verification with UI_CHECKLIST.md required!")

    if code_issues or not streamlit_ok:
        print("\n❌ REGRESSION TEST FAILED")
        sys.exit(1)
    else:
        print("\n✅ REGRESSION TEST PASSED (code patterns only)")
        sys.exit(0)


if __name__ == "__main__":
    main()
