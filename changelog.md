
# Chillin' with Chino Fitness Bot - Changelog

## v1.3 – Final Build
- Added Debug & System Logs tab in the main panel with scrollable log view.
- Added manual clear button for the active debug log.
- Weekly auto-archive of debug logs (only the most recent archive kept).
- Displayed date of last archived log and added a clickable download link in Debug tab.
- PDF exports now include a timestamped header and current app version.
- Retained all previous v1.2 fixes: universal safe inputs, failsafe resets, debug logging with highlights, and versioning.

## v1.2 – Hotfix Applied
- Added universal `safe_number_input()` for all numeric inputs (weights, age, height, workout durations, fasting, loss rate).
- Implemented a failsafe check: if any critical numeric field resolves to 0 or out-of-range, it auto-resets to pre-populated defaults.
- Added gold-highlighted warnings in debug mode for any auto-corrections or resets.
- Version tag now displayed in both sidebar and main dashboard header.
- Added logging for auto-resets to `logs/debug_log.txt` for auditability.

## v1.1 – Production Hotfix
- Implemented universal `safe_number_input()` across all numeric fields (weights, age, height, workout durations, loss rate).
- Added fasting window validation (ensures start < end, otherwise resets to default).
- Debug mode now highlights auto-corrected values in gold and logs corrections.
- Added version tagging in the sidebar ("v1.1 - Production Hotfix").
- Hardened pre-populated defaults for profile to prevent invalid data crashes.

## v1.0 – Production Hardened
- Initial production-ready release with full feature set.
- Added collapsible Quick Health Summary with calorie/protein targets, body fat %, and goal timeline.
- Integrated meal planner (fish, chicken, turkey, eggs, dairy) with grocery list and regeneration.
- Integrated personalized workout plans with images, embedded videos, and regeneration.
- Added branded PDF export (weekly summary, plans, charts, clickable links).
- Added backup & restore with auto-backup and reset to defaults.
