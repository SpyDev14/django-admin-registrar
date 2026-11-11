# Changelog

<!--
### 💥 Breaking Changes
### 🔒 Security
### ⚠️ Deprecated
### 📛 Removed
### 🐛 Fixed
### 🔁 Changed
### ✨ Added
  -->

## [Unreleased]
### 💥 Breaking Changes
- `registrars.RegisteringLogColors` moved into `dataclasses`.
- `RECCOMENDED_FORMATTER` and `RECCOMENDED_NAME` in `logging` renamed to `RECOMMENDED_*` formatter and name.
- `DefaultAdminsResolver` signature is changed. Was: `(type[Model]) -> type[ModelAdmin]`, now: `(type[Model], Any) -> type[ModelAdmin]`. Second arg (`Any`) is `config.ADMINS_FOR_MODELS`. `ADMINS_FOR_MODELS` now can be anything, and will be given as second arg to used default admins resolver.
- `AdminRegistrar._is_model_registered_already` renamed to `AdminRegistrar._is_model_registered`

### 🔁 Changed
- `COLORED_LOGS` parameter renamed to `ENABLE_COLORED_LOGS` and new default is `True` (being `False`). It is not breaking change because old default is `False`. But it enable colors in projects where colors was disabled before. You should set `ENABLE_COLORED_LOGS` to `False` id you did'nt need it.
- `AdminRegistrar` kwargs sync with used cvars

### ⚠️ Deprecated
- Rename with back compatibility. `AdminRegistrar.peform_register` to `register` for fix type (is first; was
  peForm register), and shorter name. This will be removed in future.

### ✨ Added
- `AdminRegistrar` registering now write warning on attempt to register already registered model.

## [0.2.1] - 2026-07-28
### 🐛 Fixed
- Issue #2: `first_mro_match_resolver` now does not returning base `ModelAdmin` if seen some mixin in model mro.

## [0.2.0] - 2026-07-23
### ✨ Added
- Added registering log color configuration (now only for one app, i forgot add it to conf for default)

## [0.1.0] - 2026-03-13
### ✨ Added
- Added `AdminRegistrar` with core functionality
- Added `first_mro_match_resolver` as default resolver
- Added special functionality: `HiddenAdmin` with `AdminRegistrar.hide` & `hide_several`
- Added recommended logging stuff (recommended name and formatter)
- Added draft readme
