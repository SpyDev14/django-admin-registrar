"""
Structural contracts used by the package.
"""

from typing import Any, Protocol, runtime_checkable

from django.contrib.admin import ModelAdmin
from django.db.models import Model

# DO NOT IMPORT ANY FROM admin_registrar
# for avoid circular imports

@runtime_checkable
class DefaultAdminsResolver(Protocol):
	"""Callable that picks a default admin class for a model.

	Called by `AdminRegistrar` for resolve default admin class for models, that
	are not excluded, not hidden and have no explicitly assigned admin class.
	May be a plain function, a method or an other callable instance.

	Example:
		```python
		def custom_resolver(model_class, default_admins_for_models):
			if model_class._meta.proxy:
				return ProxyModelAdmin
			return admin_registrar.config.DEFAULT_ADMINS_RESOLVER(model_class, default_admins_for_models)
		```

		```python
		# settings.py
		ADMIN_REGISTRAR = {
			"DEFAULT_ADMINS_RESOLVER": "shared.admin.resolvers.custom_resolver"
		}
		```
	"""

	def __call__(
		self,
		model_class: type[Model],
		default_admins_for_models: Any,
		/,
	) -> type[ModelAdmin]:
		"""
		Args:
			model_class: Model class to resolve an admin class for.
			default_admins_for_models: Default admins for models. In the regular
				case it is `config.ADMINS_FOR_MODELS`, but it can be overridden
				locally via `AdminRegistrar(default_admins_for_models=...)`.

		Returns:
			Admin class to register `model_class` with.
		"""
		...

@runtime_checkable
class AdminRegistry(Protocol):
	"""The abstract admin site models are registered on.

	Example:
		```python
		class CustomRegistry:
			def __init__(self, sites):
				self._sites = sites

			def register(self, model_class, admin_class):
				for site in self.sites:
					if site.is_registered(model_class):
						_logger.warning("...")
					site.register(model_class, admin_class)

			def is_registered(self, model_class) -> bool:
				return all(site.is_registered(model_class) for site in self.sites)

		registry = CustomRegistry(admin.site, other.site)
		```

		```
		# settings.py
		ADMIN_REGISTRAR = {
			"ADMIN_REGISTRY": "shared.admin.registries.registry",
		}
		```
	"""

	def register(
		self,
		model_class: type[Model],
		admin_class: type[ModelAdmin],
		/,
	) -> None:
		"""Registers the model with the given admin class.

		Args:
			model_class: Model to register.
			admin_class: Admin class for the given model.

		Raises:
			Any implementation-specific error, e.g.
			`django.contrib.admin.exceptions.AlreadyRegistered`. The caller
			checks `is_registered()` first, so this should not happen normally.
		"""
		...

	def is_registered(
		self,
		model_class: type[Model],
		/,
	) -> bool:
		"""Returns `True` if the model is already registered, else `False`.

		Args:
			model_class: Model to check.
		"""
		...
