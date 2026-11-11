from typing import Any, Protocol

from django.contrib.admin import ModelAdmin
from django.db.models import Model

# DO NOT IMPORT ANY FROM admin_registrar
# for avoid circular imports

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
