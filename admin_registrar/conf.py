from functools 	import cached_property
from typing 	import Generic, TypeVar, Self, overload

from django.utils.module_loading 	import import_string
from django.contrib.admin 			import ModelAdmin, site
from django.conf 					import settings as django_settings

from admin_registrar.resolvers 	import AdminsResolver, RegisterOnSite, first_mro_match_resolver
from admin_registrar._utils 	import typename
from admin_registrar.admin 		import HiddenAdmin

_CONFIG_DICT_NAME = 'ADMIN_REGISTRAR'
_ADMIN_REGISTRATION_CONFIG = getattr(django_settings, _CONFIG_DICT_NAME, {})
if not isinstance(_ADMIN_REGISTRATION_CONFIG, dict):
	raise TypeError(f'{_CONFIG_DICT_NAME} should be a dict, got {typename(_ADMIN_REGISTRATION_CONFIG)}.')

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

# TODO: придумать что-то, чтобы из класса настроек можно было получить доступ к объекту дескриптора (и его полям)
# Для такого: Settings.COLORED_LOGS.name
class ConfImportableValue(ConfValue[_T]):
	def _get_value(self):
		specified_path: str = _ADMIN_REGISTRATION_CONFIG.get(self._name, None)
		return (
			import_string(specified_path) if specified_path
			else self._default
		)

# TODO: Сделать нормальный конфиг
# AdminRegistrar принимает kwarg config: AdminRegistrarConfig
# AdminRegistrarConfig(*, base: AdminRegistrarConfig = admin_registrar.conf.settings, **kwargs)
# AdminRegistrarConfig(
#     ADMINS_RESOLVER = ...,
# )
# В AdminRegistrar:
#     self._conf.ADMINS_RESOLVER(model)
#     вместо
#     self._admins_resolver(model)
# Что-то такое
class Settings:
	HIDDEN_ADMIN_CLASS:       ConfImportableValue[type[ModelAdmin]] = ConfImportableValue(HiddenAdmin)
	ADMIN_CLASSES_FOR_MODELS: ConfValue[dict[str, str]]             = ConfValue({})
	ADMINS_RESOLVER:          ConfImportableValue[AdminsResolver]   = ConfImportableValue(first_mro_match_resolver)
	REGISTER_ON_SITE:         ConfImportableValue[RegisterOnSite]   = ConfImportableValue(site.register)
	COLORED_LOGS = ConfValue(False)

settings = Settings()
# settings.HIDDEN_ADMIN_CLASS
# settings.ADMIN_CLASSES_FOR_MODELS
# settings.DEFAULT_ADMINS_RESOLVER
# settings.COLORED_LOGS
# Settings.HIDDEN_ADMIN_CLASS
# Settings.ADMIN_CLASSES_FOR_MODELS
# Settings.DEFAULT_ADMINS_RESOLVER
# Settings.COLORED_LOGS
