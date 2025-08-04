
# Chillin' with Chino Fitness Bot - Changelog

## v1.3.1 – Ultimate Hotfix
- Implemented universal `safe_number_input()` for ALL numeric inputs (weights, height, age, fasting times, workout durations, loss rate).
- Pre-loaded safe defaults (start weight 230, current 228, goal 170, age 62, height 175cm) before rendering UI.
- Added startup failsafe: auto-corrects invalid/missing values before rendering any inputs.
- Debug Mode now displays and logs summary of auto-corrections made at startup.
- This build prevents any StreamlitValueBelowMinError by ensuring values always meet `min_value` before rendering.

## v1.3 – Final Build
- Added Debug & System Logs tab in the main panel with scrollable log view.
- Added manual clear button for the active debug log.
- Weekly auto-archive of debug logs (only the most recent archive kept).
- Displayed date of last archived log and added a clickable download link in Debug tab.
- PDF exports now include a timestamped header and current app version.
- Retained all previous v1.2 fixes: universal safe inputs, failsafe resets, debug logging with highlights, and versioning.
