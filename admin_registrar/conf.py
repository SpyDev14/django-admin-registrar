from typing import Generic, TypeVar, Any, Callable

from django.utils.module_loading 	import import_string
from django.contrib.admin 			import ModelAdmin
from django.db.models 				import Model
from django.conf 					import settings as django_settings

from admin_registrar._utils 	import typename
from admin_registrar 			import admin, resolvers

_CONFIG_DICT_NAME = 'ADMIN_REGISTRATOR'
_ADMIN_REGISTRATION_CONFIG = getattr(django_settings, _CONFIG_DICT_NAME, {})
if not isinstance(_ADMIN_REGISTRATION_CONFIG, dict):
	raise TypeError(f'{_CONFIG_DICT_NAME} should be a dict, got {typename(_ADMIN_REGISTRATION_CONFIG)}.')

_T = TypeVar('_T')
# Generic for default type hints (if not specified)
class ConfigValue(Generic[_T]):
	def __set_name__(self, name: str):
		self._name = name

	def __init__(self, default: _T):
		self._default: _T = default

	def __get__(self, instance, owner: type | None = None) -> _T:
		value = _ADMIN_REGISTRATION_CONFIG.get(self._name, self._default)
		setattr(instance, self._name, value)
		return value

# TODO: придумать что-то, чтобы из класса настроек можно было получить доступ к объекту дескриптора (и его полям)
# Для такого: Settings.COLORED_LOGS.name
class ConfigImportableValue(ConfigValue): # Generic not need, else need write a ConfigValue[_T]
	def __get__(self, instance, object_type = None) -> Any:
		specified_path: str = _ADMIN_REGISTRATION_CONFIG.get(self._name, None)
		value = (
			import_string(specified_path) if specified_path
			else self._default
		)
		setattr(instance, self._name, value)
		return value


class Settings:
	HIDDEN_ADMIN_CLASS: type[ModelAdmin] = ConfigImportableValue(admin.HiddenAdmin)
	ADMIN_CLASSES_FOR_MODELS: dict[str, str] = ConfigValue({})
	DEFAULT_ADMINS_RESOLVER: resolvers.AdminsResolver \
		= ConfigImportableValue(resolvers.first_mro_match_resolver)
	COLORED_LOGS = ConfigValue(False)

admin_reg_settings = Settings()
