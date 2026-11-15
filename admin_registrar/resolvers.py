from typing import Any, Mapping

from django.utils.module_loading import import_string
from django.contrib.admin import ModelAdmin
from django.db.models import Model

from admin_registrar.internal import typename


_fmmr_cache: dict[frozenset, Mapping[type[Model], type[ModelAdmin]]] = {}
def first_mro_match_resolver(model_class: type[Model], default_admins_for_models: Any) -> type[ModelAdmin]:
	base_err_msg = (
		f"given default_admins_for_models for "
		f"{first_mro_match_resolver.__name__} "
		f"should be Mapping[str, str]"
	)

	if not isinstance(default_admins_for_models, Mapping):
		raise TypeError(f"{base_err_msg}, got: {typename(default_admins_for_models)}.")

	try:
		cache_key = frozenset(default_admins_for_models.items())
	except TypeError:
		cache_key = None

	if cache_key is not None and cache_key in _fmmr_cache:
		parsed = _fmmr_cache[cache_key]
	else:
		parsed = {}
		for i, (key, value) in enumerate(default_admins_for_models.items()):
			if not isinstance(key, str):
				raise TypeError(f"{base_err_msg}, got mapping where key is {typename(key)} (position is {i}).")
			if not isinstance(value, str):
				raise TypeError(f"{base_err_msg}, got mapping where value is {typename(value)} (position is {i}).")
			parsed[import_string(key)] = import_string(value)

		if cache_key is not None:
			_fmmr_cache[cache_key] = parsed

	for cls in model_class.mro():
		if not issubclass(cls, Model):
			continue  # model can nest some mixins
		if cls in parsed:
			return parsed[cls]
	return ModelAdmin
