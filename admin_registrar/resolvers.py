from weakref import WeakKeyDictionary
from typing import Any, Mapping

from django.utils.module_loading import import_string
from django.contrib.admin import ModelAdmin
from django.db.models import Model

from admin_registrar.internal import typename
from admin_registrar.types import DefaultAdminsResolver


_fmmr_cache: WeakKeyDictionary[object, Mapping[type[Model], type[ModelAdmin]]] = WeakKeyDictionary()
def first_mro_match_resolver(model_class: type[Model], default_admins_for_models: Any) -> type[ModelAdmin]:
	if default_admins_for_models not in _fmmr_cache:
		data = default_admins_for_models
		base_err_msg = (
			f"given default_admins_for_models for " +
			first_mro_match_resolver.__name__ +
			" should be Mapping[str, str]"
		)

		if not isinstance(data, Mapping):
			raise TypeError(f"{base_err_msg}, got: {typename(data)}.")

		parsed = {}
		for i, (key, value) in enumerate(data.items()):
			if not isinstance(key, str): raise TypeError(
				f"{base_err_msg}, got mapping where key is {typename(key)} (position is {i})."
			)
			if not isinstance(value, str): raise TypeError(
				f"{base_err_msg}, got mapping where value is {typename(value)} (position is {i})."
			)
			parsed[import_string(key)] = import_string(value)
		_fmmr_cache[data] = parsed

	for cls in model_class.mro():
		if not issubclass(cls, Model):
			continue # model can nest some mixins
		if cls in _fmmr_cache[default_admins_for_models]:
			return _fmmr_cache[default_admins_for_models][cls]
	return ModelAdmin
