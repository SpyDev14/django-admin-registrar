from dataclasses import is_dataclass
from functools import cached_property
from typing import Generic, TypeVar, Self, overload, Any, TYPE_CHECKING
import logging

from django.utils.module_loading import import_string
from django.contrib.admin import ModelAdmin
from django.db.models import Model
from django.conf import settings as django_settings

from admin_registrar.utils import typename

if TYPE_CHECKING:
	from admin_registrar.dataclasses import RegisteringLogColors
	from admin_registrar.resolvers import DefaultAdminsResolver


_CONFIG_DICT_NAME = 'ADMIN_REGISTRAR'
_CONFIG_DICT: dict[str, Any] = getattr(django_settings, _CONFIG_DICT_NAME, {})
if not isinstance(_CONFIG_DICT, dict):
	raise TypeError(f'{_CONFIG_DICT_NAME} should be a dict, got: {typename(_CONFIG_DICT)}.')

_T = TypeVar('_T')
# Generic for default type hints (if not specified)
class ConfVar(Generic[_T]):
	def __set_name__(self, owner: type, name: str):
		self._name = name

	def __init__(self, raw_default: Any):
		self._raw_default = raw_default

	def __str__(self):
		return self._name

	@cached_property
	def _value(self):
		return self._get_value()

	def _get_value(self):
		return _CONFIG_DICT.get(self._name, self._raw_default)

	@overload
	def __get__(self, instance: None, owner: type) -> Self: ...
	@overload
	def __get__(self, instance: object, owner: type) -> _T: ...
	def __get__(self, instance: object | None, owner: type) -> Self | _T:
		if not instance:
			return self
		return self._value

class ImportableConfVar(ConfVar[_T]):
	def __init__(self, raw_default: str):
		super().__init__(raw_default)
		self._raw_default: str

	def _get_value(self):
		import_str = _CONFIG_DICT.get(self._name)
		if import_str is not None and not isinstance(import_str, str):
			raise TypeError(f"Importable {self._name} shoud be a string")

		return import_string(import_str or self._raw_default)

class DataclassConfVar(ConfVar[_T]):
	def __init__(self, raw_default: dict[str, Any], dataclass_import_str: str):
		super().__init__(raw_default)
		self._raw_default: dict[str, Any]
		self._dataclass_import_str = dataclass_import_str

	def _import_dataclass(self):
		imported = import_string(self._dataclass_import_str)
		if not isinstance(imported, type) or not is_dataclass(imported):
			raise TypeError(f"{typename(imported)} isn't dataclass")
		return imported

	def _get_value(self):
		data = _CONFIG_DICT.get(self._name, self._raw_default)

		if not isinstance(data, dict):
			raise TypeError(f"{self._name} should be a dict, got: {typename(data)}")

		dataclass = self._import_dataclass()
		return dataclass(**data)

class ImportablesDictConfVar(ConfVar[_T]):
	def __init__(self, raw_default: dict[str, str]):
		super().__init__(raw_default)
		self._raw_default: dict[str, str]

	def _get_value(self):
		data: dict[str, str] = _CONFIG_DICT.get(self._name, self._raw_default)
		if not isinstance(data, dict):
			raise TypeError(f"{self._name} should be a dict, got: {typename(data)}")

		return {
			import_string(key): import_string(value)
			for key, value in data.items()
		}

# Settings can be refactored to `Config` with `base` and
# values-nesting for global defaults and local overrides
class Settings:
	HIDDEN_ADMIN_CLASS: ImportableConfVar[type[ModelAdmin]] = ImportableConfVar('admin_registrar.admin.HiddenAdmin')
	# ADMINS_FOR_MODELS used only in admin_registrar resolvers by directly get from settings
	# Maybe should refactor it for future allowing custom rules?
	# Like "core.models.base.BaseRenderableModel+mptt.models.MPTTModel": "core.admin.base.RenderableMPTTAdmin"
	# what catch models who mro is [BaseRenderableModel, MPTTModel, ...]
	ADMINS_FOR_MODELS: ImportablesDictConfVar[dict[type[Model], type[ModelAdmin]]] = ImportablesDictConfVar({})
	ENABLE_COLORED_LOGS: ConfVar[bool] = ConfVar(True)

	DEFAULT_ADMINS_RESOLVER: ImportableConfVar["DefaultAdminsResolver"] = ImportableConfVar('admin_registrar.resolvers.first_mro_match_resolver')
	REGISTERING_LOG_COLORS: DataclassConfVar["RegisteringLogColors"] = DataclassConfVar({}, 'admin_registrar.dataclasses.RegisteringLogColors')
	REGISTERING_LOG_LEVEL: ConfVar[int] = ConfVar(logging.DEBUG)

settings = Settings()
