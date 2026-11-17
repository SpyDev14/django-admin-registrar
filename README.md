# Django Admin Registrar
> Has russian-locale readme version below / Есть версия на русском языке ниже

1. [Last changes](#the-great-030-release-is-here)
2. [About package](#about-package)
3. [Roab-map to v1.0](#road-map-to-v10)

## The great **0.3.0** release is here!
### ✨ Added
- `AdminRegistrar` registering now write warning on attempt to register already registered model.
- Added `AdminRegistry` type: now you can specify special admin registry for register models in admin site (before `django.contrib.admin:site` was used directly).
- Added `AdminRegistry.defer_registration`: now you can defer registration to App ready event (`YourAppConfig.ready` method will be wrapped). Previously this had to be done manually.
- Added `Config` local overrides support: now you cah pass partial overrided `Config` to `AdminRegister` instead kwargs.
- Added check for unknown keys in `settings.ADMIN_REGISTRAR` config dict.
- Added application init check validation of all given cvars (for fast fail).

### 🔁 Changed
- `COLORED_LOGS` parameter renamed to `ENABLE_COLORED_LOGS` and new default is `True` (being `False`). It is not breaking change because old default is `False`. But it enable colors in projects where colors was disabled before. You should set `ENABLE_COLORED_LOGS` to `False` id you did'nt need it. You see a warning if `COLORED_LOGS` in your config dict (unknown key warning).
- Attempt to re-register admins by AdminRegistrar now throws `RuntimeError`.

## About package
This package simplifies the registration of Django models in the admin site. It registers all models of a given app (`AppConfig`), allowing you to define default admin classes (`ModelAdmin`) for models and avoid having to manually register each newly added model according to project-wide rules. For example, instead of manually registering every `SingletonModel` subclass (from `django-solo`) with `SingletonModelAdmin`, you can specify in the package settings:

```python
# settings.py
ADMIN_REGISTRAR = {
    'ADMINS_FOR_MODELS': {
        'solo.models.SingletonModel': 'solo.admin.SingletonModelAdmin'
    }
}
```
```python
# admin.py
from admin_registrar import AdminRegistrar
from src.apps.products.apps import ProductsConfig

registrar = AdminRegistrar(ProductsConfig)
registrar.register()
```

Now, by default, all `SingletonModel` subclasses will be registered with `SingletonModelAdmin`.

The package also offers an additional feature: "hidden models". This is a special shortcut for registering a model with `HiddenAdmin` – a custom admin class that registers the model in the admin panel but does not display it in the list, allowing all CRUD operations on the model without cluttering the main model list. This is useful when you have models like "Product Characteristic Type" and "Product Characteristic" that are only used within a product, and you want to create/edit/delete them from the product change form.

For configuring autoregister `AdminRegistrar` has too many methods (and decorators). Enjoy!

## Road-map to v1.0
- Adding a normal docs (docstrings and re-docs)
- Adding a tests (manual testing is bruh)
- Adding cool default admins resolver with advanced model specifiers (like `OrderedModel` + `MPTTModel` -> `OrderedMPTTModelAdmin`) and admin auto-generating (`OrderedModel` + `MPTTModel` -> `OrderedModelAdmin` + `MPTTModelAdmin`)
- Add "Patch" admins, instead `set_admin_for_model`, for use combination of explicit admin class and implicit default admin (by specifiers).
