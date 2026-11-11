from typing import Any, Protocol, runtime_checkable

from django.contrib.admin import ModelAdmin
from django.db.models import Model

# DO NOT IMPORT ANY FROM admin_registrar
# for avoid circular imports

@runtime_checkable
class DefaultAdminsResolver(Protocol):
	def __call__(
		self,
		model_class: type[Model],
		default_admins_for_models: Any,
		/,
	) -> type[ModelAdmin]:
		"""
		Args:
			model_class:
				Model to resolving.
			default_admins_for_models:
				Default admins for models. In regular case, is
				`config.ADMINS_FOR_MODELS`, but can be local overridden.
		"""
		...

@runtime_checkable
class AdminRegistry(Protocol):
	def register(
		self,
		model_class: type[Model],
		admin_class: type[ModelAdmin],
		/,
	) -> None:
		"""
		Args:
			model_class: Model to register.
			admin_class: Admin class for given model.
		d"""
		...

	def is_registered(
		self,
		model_class: type[Model],
		/,
	) -> bool:
		"""
		Returns `True` if model already registered, else `False`.

		Args:
			model_class: Model to check.
		"""
		...
