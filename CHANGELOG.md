# Changelog
## [Unreleased]
### 💥 Breaking Changes
- `registrars.RegisteringLogColors` moved into `dataclasses` for fix Circular Import in `conf`.
- `RECCOMENDED_*` formatter and name in `logging.py` renamed to `RECOMMENDED_*` formatter and name.

### ✨ Added
- Added registering global log color configuration for the entire project (instead of per‑app only).
- `AdminRegistrar.registering_log_level` default now getting from `settings.REGISTERING_LOG_LEVEL`
- `AdminRegistrar.registering_log_colors` default now getting from `settings.REGISTERING_LOG_COLORS`

### 🔁 Changed
- `COLORED_LOGS` parameter renamed to `ENABLE_COLORED_LOGS` and new default is `True` (being `False`).

### ⚠️ Deprecated
- Fixed type in `AdminRegistrar.peform_register` name, now `perform_register` (peRform instead peForm)
  with back compatibility. Will be removed in future.

<!--
### 💥 Breaking Changes
### 🔒 Security
### ⚠️ Deprecated
### 📛 Removed
### 🐛 Fixed
### 🔁 Changed
### ✨ Added
  -->

## [0.2.1] - 2026-07-28
### 🐛 Fixed
- Issue #2: `first_mro_match_resolver` now does not returning base `ModelAdmin` if seen some mixin in model mro.

## [0.2.0] - 2026-07-23
### ✨ Added
- Added registering log color configuration (now only for one app, i forgot add it to conf for default)

## [0.1.0] - 2026-03-13
### ✨ Added
- Added core features (`AdminRegistrar`, `first_mro_match_resolver`, and other; lazy enumerate; added
  before changelog was added), project is started and can be used in projects
- Added `AdminRegistrar` with core functionality
- Added `first_mro_match_resolver` as default resolver
- Added special functionality: `HiddenAdmin` with `AdminRegistrar.hide` & `hide_several`
- Added recommended logging stuff (recommended name and formatter)
- Added draft readme
