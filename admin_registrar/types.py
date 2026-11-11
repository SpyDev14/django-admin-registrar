from typing import Any, Protocol

from django.contrib.admin import ModelAdmin
from django.db.models import Model

# DO NOT IMPORT ANY FROM admin_registrar
# for avoid circular imports

class DefaultAdminsResolver(Protocol):
	def __call__(
		self,
		model_class: type[Model],
		admins_for_models: Any
	) -> type[ModelAdmin]:
		"""
		Args:
			model_class: model to resolving
			admins_for_models: given from AdminRegistrar (can be overrided).
				In regular case is `config.ADMINS_FOR_MODELS`.
		"""
		...
