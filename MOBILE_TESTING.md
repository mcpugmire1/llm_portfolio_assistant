# Mobile Responsiveness Testing Guide

This branch (`feature/mobile-responsive-ui`) contains mobile/tablet responsive CSS that you can safely test without affecting your main branch.

## 📱 What's Included

### 1. **Wireframes** (Reference Only)
- **[WIREFRAMES.md](WIREFRAMES.md)**: ASCII wireframes for all 5 pages × 3 devices
- **[wireframes_visual.html](wireframes_visual.html)**: Interactive HTML preview
  - Open in browser: `open wireframes_visual.html`
  - Switch between devices, pages, and light/dark modes

### 2. **Mobile CSS** (Ready to Test)
- **[ui/styles/mobile_overrides.py](ui/styles/mobile_overrides.py)**: 622 lines of responsive CSS
  - Mobile (<768px): 48px avatars, 1-column grids, stacked layouts
  - Tablet (768-1023px): 64px avatars, 2-column grids
  - Desktop (1024px+): Unchanged (your existing CSS)

### 3. **Enable/Disable Script** (Safety Tool)
- **[scripts/enable_mobile_css.py](scripts/enable_mobile_css.py)**: Toggle mobile CSS on/off

---

## 🧪 Safe Testing Workflow

### Step 1: Check Status (Currently Disabled)
```bash
python3 scripts/enable_mobile_css.py --status
```

**Output:**
```
Mobile CSS Status: DISABLED ❌
```

---

### Step 2: Preview Wireframes (No Risk)
Open the visual wireframes in your browser:

```bash
open wireframes_visual.html
```

**What you'll see:**
- All 5 pages (Home, Landing, Conversation, Explore Stories, About Matt)
- Switch devices: iPhone SE (375px), iPhone 14 (430px), iPad (768px), Desktop (1024px)
- Toggle dark mode
- Real Agy avatars, purple gradients, proper responsive behavior

**This is just a preview** - your actual app is unchanged.

---

### Step 3: Enable Mobile CSS in Real App
When you're ready to test the actual Streamlit app with mobile responsiveness:

```bash
python3 scripts/enable_mobile_css.py --enable
```

**What this does:**
- Injects 4 lines into `ui/styles/global_styles.py`:
  ```python
  # Mobile responsive CSS overrides
  from ui.styles.mobile_overrides import get_mobile_css
  st.markdown(get_mobile_css(), unsafe_allow_html=True)
  ```

**Output:**
```
✅ Mobile CSS enabled successfully!
   Run your Streamlit app to see responsive behavior at <768px
```

---

### Step 4: Test the App
Run your Streamlit app normally:

```bash
streamlit run app.py
```

**Then test responsiveness:**

1. **Chrome DevTools Method:**
   - Open app in browser
   - Press `Cmd+Option+I` (Mac) or `F12` (Windows)
   - Click "Toggle device toolbar" icon (phone/tablet icon)
   - Select device: iPhone SE, iPhone 14 Pro Max, iPad

2. **Physical Device Method:**
   - Run app: `streamlit run app.py --server.address 0.0.0.0`
   - On your iPhone/iPad, navigate to: `http://YOUR_COMPUTER_IP:8501`

**What to test:**
- [ ] Header shrinks to 48px avatar on mobile
- [ ] "How Agy Searches" becomes icon-only (🔍) on mobile
- [ ] Suggestion buttons stack in 1 column on mobile
- [ ] Chat avatars shrink to 40px on mobile
- [ ] Status bar shows abbreviated text on mobile
- [ ] All pages work at 375px, 768px, and 1024px

---

### Step 5: Disable If Issues Found
If you encounter problems, instantly revert:

```bash
python3 scripts/enable_mobile_css.py --disable
```

**Output:**
```
✅ Mobile CSS disabled successfully!
   App will return to desktop-only mode
```

**This removes the 4 lines** from `global_styles.py` - your app is back to normal.

---

## 🔍 What Gets Changed

### When DISABLED (default):
```python
# ui/styles/global_styles.py
def apply_global_styles():
    st.markdown("""<style>...existing CSS...</style>""", unsafe_allow_html=True)
    # ← Nothing mobile-related here
```

### When ENABLED:
```python
# ui/styles/global_styles.py
def apply_global_styles():
    st.markdown("""<style>...existing CSS...</style>""", unsafe_allow_html=True)

    # Mobile responsive CSS overrides  ← Added
    from ui.styles.mobile_overrides import get_mobile_css  ← Added
    st.markdown(get_mobile_css(), unsafe_allow_html=True)  ← Added
```

**That's it** - no other files are touched.

---

## 📊 Responsive Breakpoints

| Viewport | Behavior | Avatar Size | Grid Layout |
|----------|----------|-------------|-------------|
| **<768px** (Mobile) | Stacked, 1-column | 40-48px | 1 column |
| **768-1023px** (Tablet) | 2-column grids | 56-64px | 2 columns |
| **1024px+** (Desktop) | Unchanged (your existing CSS) | 60-64px | 3 columns |

---

## 🐛 Troubleshooting

### "Mobile CSS doesn't seem to work"
1. Check browser width: Must be <768px to trigger mobile styles
2. Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+F5` (Windows)
3. Check status: `python3 scripts/enable_mobile_css.py --status`

### "App looks broken on mobile"
1. Disable immediately: `python3 scripts/enable_mobile_css.py --disable`
2. Check which page is broken (Home, Landing, Conversation, etc.)
3. Open wireframes_visual.html to see expected behavior
4. Report specific issue (e.g., "Chat bubbles overlap at 375px")

### "Want to go back to main branch"
```bash
# Save your testing notes (optional)
git add -A
git commit -m "test: mobile CSS testing notes"

# Switch back to stable main branch
git checkout main

# Mobile CSS is NOT on main branch - app is safe
```

---

## ✅ Next Steps

1. **Preview wireframes first**: `open wireframes_visual.html`
2. **Enable mobile CSS**: `python3 scripts/enable_mobile_css.py --enable`
3. **Test on real devices**: iPhone SE, iPad
4. **Disable if needed**: `python3 scripts/enable_mobile_css.py --disable`

**When satisfied:**
```bash
# Commit your testing results
git add -A
git commit -m "test: verified mobile responsiveness works"

# Merge to main (or create PR for review)
git checkout main
git merge feature/mobile-responsive-ui
```

---

## 🔒 Safety Guarantees

✅ **Main branch is untouched** - mobile CSS only exists on this feature branch
✅ **Desktop mode unchanged** - mobile CSS only activates at <768px
✅ **Instant rollback** - disable script removes mobile CSS in 1 command
✅ **No data loss** - CSS-only changes, no database/file modifications

**You can always return to stable main branch with:**
```bash
git checkout main
```
