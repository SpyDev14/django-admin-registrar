from django.utils.module_loading 	import import_string
from django.contrib.admin 			import ModelAdmin
from django.db.models 				import Model

from admin_registrar.conf import admin_reg_settings

# caching
_PARSED_DEFAULTS: dict[type[Model], type[ModelAdmin]] = {}
def first_mro_match_resolver(model_class: type[Model]) -> type[ModelAdmin]:
	if not _PARSED_DEFAULTS:
		_PARSED_DEFAULTS = {
			import_string(model_path): import_string(admin_path)
			for model_path, admin_path in
			admin_reg_settings.DEFAULT_ADMIN_CLASSES.items()
		}

	for cls in model_class.mro():
		if not issubclass(cls, Model):
			return ModelAdmin
		if cls in _PARSED_DEFAULTS:
			return _PARSED_DEFAULTS[cls]

	return ModelAdmin
