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

<!-- ## [Unreleased] -->
## [0.3.1] - 2026-11-17
### 🐛 Fixed
- Fixed "is hidden" detect in making log message in `AdminRegistrar._try_register_on_site`

## [0.3.0] - 2026-11-16
### 💥 Breaking Changes
- `AdminRegistrar.__init__` kwargs dublicate `Config` cvars was removed, use `config` by `config.with_overrides(...)`.
- `DefaultAdminsResolver` signature is changed. Was: `(type[Model]) -> type[ModelAdmin]`, now: `(type[Model], Any) -> type[ModelAdmin]`. Second arg (`Any`) is `config.ADMINS_FOR_MODELS`. `ADMINS_FOR_MODELS` now can be anything, and will be given as second arg to used default admins resolver.
- `AdminRegistrar._app` renamed to `_app_class` (reminder: `_x` is `protected`, not `private`, can be used in child classes)
- `AdminRegistrar._is_model_registered_already` renamed to `AdminRegistrar._is_model_registered`
- `registrars.RegisteringLogColors` moved into `dataclasses`.
- `RECCOMENDED_FORMATTER` and `RECCOMENDED_NAME` in `logging` renamed to `RECOMMENDED_*` formatter and name.
- Argument `admins_for_models` of `DefaultAdminsResolver.__call__` now positional-only (and renamed to `default_admins_for_models`, bot it does't matter).
- Argument `model_class` of `DefaultAdminsResolver.__call__` now positional-only.
- `logging.RECOMMENDED_NAME` was removed. Use `admin_registrar.registrars` directly.

### 🔁 Changed
- `COLORED_LOGS` parameter renamed to `ENABLE_COLORED_LOGS` and new default is `True` (being `False`). It is not breaking change because old default is `False`. But it enable colors in projects where colors was disabled before. You should set `ENABLE_COLORED_LOGS` to `False` id you did'nt need it. You have seen warning
- Attempt to re-register admins by AdminRegistrar now throws `RuntimeError`.

### ⚠️ Deprecated
- Rename with back compatibility `AdminRegistrar.peform_register` to `register` for fix type (is first; was peForm register), and shorter name. This will be removed in `v1.0.0`.

### ✨ Added
- `AdminRegistrar` registering now write warning on attempt to register already registered model.
- Added `AdminRegistry` type: now you can specify special admin registry for register models in admin site (before `django.contrib.admin:site` was used directly).
- Added `AdminRegistry.defer_registration`: now you can defer registration to App ready event (`YourAppConfig.ready` method will be wrapped). Previously this had to be done manually.
- Added `Config` local overrides support: now you cah pass partial overrided `Config` to `AdminRegister` instead kwargs.
- Added check for unknown keys in `settings.ADMIN_REGISTRAR` config dict.
- Added application init check validation of all given cvars (for fast fail).

## [0.2.3] - 2026-11-16
### Fixed
- `AdminRegistrar._get_models_to_register` now uses `self._app.label` instead `self._app.name` to get app, because `apps.get_app_config` store apps by `label`, not by `name`.

## [0.2.2] - 2026-11-16
Revoked because contain ctitical error

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
