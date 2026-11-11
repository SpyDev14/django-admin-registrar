from typing import Any, Mapping

from django.utils.module_loading import import_string
from django.contrib.admin import ModelAdmin
from django.db.models import Model

from admin_registrar.internal import typename
from admin_registrar.conf import Config, config

_PARSED_ADMINS_FOR_MODELS_CACHE: Mapping[type[Model], type[ModelAdmin]] | None = None
def first_mro_match_resolver(model_class: type[Model], admins_for_models: Any) -> type[ModelAdmin]:
	if _PARSED_ADMINS_FOR_MODELS_CACHE is None:
		global _PARSED_ADMINS_FOR_MODELS_CACHE
		data: Mapping[str, str] = admins_for_models
		base_err_msg = (
			str(Config.ADMINS_FOR_MODELS) if admins_for_models is config.ADMINS_FOR_MODELS
			else "given admins_for_models"
			f"for {first_mro_match_resolver.__name__}"
			" should be Mapping[str, str]"
		)

		if not isinstance(data, Mapping):
			raise TypeError(f"{base_err_msg}, got: {typename(data)}.")

		parsed = _PARSED_ADMINS_FOR_MODELS_CACHE = {}
		for i, (key, value) in enumerate(data.items()):
			if not isinstance(key, str): raise TypeError(
				f"{base_err_msg}, got mapping key type is {typename(key)} (position is {i})."
			)
			if not isinstance(value, str): raise TypeError(
				f"{base_err_msg}, got mapping value type is {typename(value)} (position is {i})."
			)
			parsed[import_string(key)] = import_string(value)

	for cls in model_class.mro():
		if not issubclass(cls, Model):
			continue # model can nest some mixins
		if cls in _PARSED_ADMINS_FOR_MODELS_CACHE:
			return _PARSED_ADMINS_FOR_MODELS_CACHE[cls]
	return ModelAdmin
