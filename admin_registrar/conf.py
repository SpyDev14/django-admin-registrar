from typing import Generic, TypeVar, Any

from django.utils.module_loading 	import import_string
from django.contrib.admin 			import ModelAdmin
from django.conf 					import settings as django_settings

from admin_registrar.utils 	import typename
from admin_registrar 			import admin

_CONFIG_DICT_NAME = 'ADMIN_REGISTRATOR'
_ADMIN_REGISTRATION_CONFIG = getattr(django_settings, _CONFIG_DICT_NAME, {})
if not isinstance(_ADMIN_REGISTRATION_CONFIG, dict):
	raise TypeError(f'{_CONFIG_DICT_NAME} should be a dict, got {typename(_ADMIN_REGISTRATION_CONFIG)}.')

_T = TypeVar('_T')
# Generic for tips by default type
class ConfigValue(Generic[_T]):
	def __set_name__(self, name: str):
		self._name = name

	def __init__(self, default: _T):
		self._default: _T = default

	def __get__(self, obj, object_type = None) -> _T:
		value = _ADMIN_REGISTRATION_CONFIG.get(self._name, self._default)
		setattr(obj, self._name, value)
		return value

class ConfigImportableValue:
	def __set_name__(self, name: str):
		self._name = name

	def __init__(self, default: Any):
		self._default = default

	def __get__(self, obj, object_type = None) -> Any:
		specified_path: str = _ADMIN_REGISTRATION_CONFIG.get(self._name, None)
		value = (
			import_string(specified_path) if specified_path
			else self._default
		)
		setattr(obj, self._name, value)
		return value


class Settings:
	HIDDEN_ADMIN_CLASS: type[ModelAdmin] = ConfigImportableValue(admin.HiddenAdmin)
	DEFAULT_ADMIN_CLASSES: dict[str, str] = ConfigValue({})
	COLORED_LOGS = ConfigValue(False)

admin_reg_settings = Settings()
