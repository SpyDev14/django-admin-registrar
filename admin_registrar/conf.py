from functools import cached_property
from typing import Generic, TypeVar, Self, overload, Any

from django.utils.module_loading import import_string
from django.contrib.admin import ModelAdmin
from django.conf import settings as django_settings

from admin_registrar.resolvers import DefaultAdminsResolver, first_mro_match_resolver
from admin_registrar.utils import typename
from admin_registrar.admin import HiddenAdmin

_CONFIG_DICT_NAME = 'ADMIN_REGISTRAR'
_ADMIN_REGISTRATION_CONFIG: dict[str, Any] = getattr(django_settings, _CONFIG_DICT_NAME, {})
if not isinstance(_ADMIN_REGISTRATION_CONFIG, dict):
	raise TypeError(f'{_CONFIG_DICT_NAME} should be a dict, got: {typename(_ADMIN_REGISTRATION_CONFIG)}.')

_T = TypeVar('_T')
# Generic for default type hints (if not specified)
class ConfValue(Generic[_T]):
	def __set_name__(self, owner: type, name: str):
		self._name = name

	def __init__(self, default: _T):
		self._default = default

	def __str__(self):
		return self._name

	@cached_property
	def _value(self):
		return self._get_value()

	def _get_value(self):
		return _ADMIN_REGISTRATION_CONFIG.get(self._name, self._default)

	@overload
	def __get__(self, instance: None, owner: type) -> Self: ...
	@overload
	def __get__(self, instance: object, owner: type) -> _T: ...
	def __get__(self, instance: object | None, owner: type) -> Self | _T:
		if not instance:
			return self
		return self._value

class ConfImportableVal(ConfValue[_T]):
	def _get_value(self):
		specified_path = _ADMIN_REGISTRATION_CONFIG.get(self._name)
		if specified_path is not None and not isinstance(specified_path, str):
			raise TypeError(f"Importable {self._name} shoud be a string")
		return (
			import_string(specified_path) if specified_path
			else self._default
		)

# Settings can be refactored to `Config` with `base` property and
# values-nesting for global defaults and local overrides
class Settings:
	# DEFAULT_ADMINS_RESOLVER can be refactored!!!
	DEFAULT_ADMINS_RESOLVER: ConfImportableVal[DefaultAdminsResolver] = ConfImportableVal(first_mro_match_resolver)
	HIDDEN_ADMIN_CLASS:      ConfImportableVal[type[ModelAdmin]]      = ConfImportableVal(HiddenAdmin)
	ADMINS_FOR_MODELS = ConfValue({})
	COLORED_LOGS      = ConfValue(False)

settings = Settings()
