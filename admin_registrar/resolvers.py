from typing import Protocol

from django.utils.module_loading import import_string
from django.contrib.admin import ModelAdmin
from django.db.models import Model

# Circular import
# from admin_registrar.conf import settings


class DefaultAdminsResolver(Protocol):
	def __call__(self, model_class: type[Model]) -> type[ModelAdmin]: ...

# caching
_PARSED_DEFAULTS: dict[type[Model], type[ModelAdmin]] = {}
def first_mro_match_resolver(model_class: type[Model]) -> type[ModelAdmin]:
	from admin_registrar.conf import settings
	global _PARSED_DEFAULTS

	if not _PARSED_DEFAULTS:
		_PARSED_DEFAULTS = {
			import_string(model_path): import_string(admin_path)
			for model_path, admin_path in
			settings.ADMINS_FOR_MODELS.items()
		}

	for cls in model_class.mro():
		if not issubclass(cls, Model):
			continue # If model nesting from some mixins who not nested from Model
		if cls in _PARSED_DEFAULTS:
			return _PARSED_DEFAULTS[cls]

	return ModelAdmin
