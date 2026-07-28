# Changelog

## [0.2.1] - 2026-07-28
### Fixed
- `first_mro_match_resolver` now does not returning base `ModelAdmin` if seen some mixin in model mro.

## [0.2.0] - 2026-07-23
### Added
- Added registering log color configuration (now only for one app, i forgot add it to conf for default)

## [0.1.0] - 2026-03-13
### Added
- Added core features (`AdminRegistrar`, `first_mro_match_resolver`, and other; lazy enumerate; added
  before changelog was added), project is started and can be used in projects
- Added `AdminRegistrar` with core functionality
- Added `first_mro_match_resolver` as default resolver
- Added special functionality: `HiddenAdmin` with `AdminRegistrar.hide` & `hide_several`
- Added recommended logging stuff (recommended name and formatter)
- Added draft readme
