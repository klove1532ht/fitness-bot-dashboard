
# Chillin' with Chino Fitness Bot - Changelog

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
