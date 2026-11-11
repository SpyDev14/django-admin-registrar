from dataclasses import dataclass, is_dataclass
from typing import (
	Callable, Generic, Mapping, NoReturn, Sequence, TypeAlias,
	TypeVar, Self, overload, Any, TYPE_CHECKING, cast
)
from copy import deepcopy
import logging

from django.utils.module_loading import import_string
from django.contrib.admin import ModelAdmin
from django.conf import settings as django_settings
import django.contrib.admin

from admin_registrar.internal.unset import UNSET, UnsetT
from admin_registrar.internal.types import IterableAbstractSet, one_or_seq_to_seq
from admin_registrar.internal import typename
from admin_registrar.internal.verbose import verb_list
from admin_registrar.types import DefaultAdminsResolver

if TYPE_CHECKING:
	from admin_registrar.dataclasses import RegisteringLogColors


_CONFIG_DICT_NAME = 'ADMIN_REGISTRAR'
def _get_config_dict() -> dict[str, Any]:
	"""ALLOWED INTERNAL IMPORT"""
	config_dict = getattr(django_settings, _CONFIG_DICT_NAME, {})
	if not isinstance(config_dict, dict):
		raise TypeError(f'{_CONFIG_DICT_NAME} should be a dict, got: {typename(config_dict)}.')

	for key in config_dict.keys():
		assert isinstance(key, str)

	return config_dict

_T = TypeVar('_T')

class _TypeRef(Generic[_T]):
	def __init__(self, class_or_import_path: type[_T] | str):
		self._class_or_import_path = class_or_import_path

	def resolve(self) -> type[_T]:
		if isinstance(self._class_or_import_path, str):
			return cast(type[_T], import_string(self._class_or_import_path))
		return self._class_or_import_path

# maked for type checks in CVar (i plane to separate CVar & processors to
# internal.configuring in the future)
class _BaseConfig:
	@classmethod
	def _get_known_keys_for_conf_dict(cls) -> set[str]:
		"""FOR INTERNAL USE, NOT PROTECTED"""
		return {
			attr_name for attr_name in dir(cls)
			if not attr_name.startswith('_') and
			isinstance(getattr(cls, attr_name), _CVar)
		}

# MARK: CVar def
@dataclass
class _CVarInfo:
	name: str


_CVarProcessor: TypeAlias = Callable[[Any, _CVarInfo], Any | NoReturn]
_CVarValidator: TypeAlias = Callable[[Any, _CVarInfo], None | NoReturn]

class _CVar(Generic[_T]):
	@overload
	def __init__(self, *,
		default: _T,
		validators: Sequence[_CVarValidator]): ...
	@overload
	def __init__(self, *,
		default_factory: Callable[[], _T],
		validators: Sequence[_CVarValidator]): ...
	@overload
	def __init__(self, *,
		raw_default: Any,
		processors: Sequence[_CVarProcessor],
		validators: Sequence[_CVarValidator]): ...

	def __init__(self,
		*,
		default: _T | UnsetT = UNSET, # if value immutable (bool, int, str, etc.)
		default_factory: Callable[[], _T] | None = None, # if value mutable (recommended in regular case)
		raw_default: Any | None = None, # if circular import problem
		# process given raw value. doesn't need for some bool, int and other.
		processors: Sequence[_CVarProcessor] = (),
		# validate CVar get_value result is correct: check type, check value, etc.
		validators: Sequence[_CVarValidator],
	) -> None:
		match (sum((default is not UNSET, default_factory is not None, raw_default is not None))):
			case 0: raise ValueError(f"Default value for CVar should be specified")
			case 1: pass
			case _: raise ValueError(f"Default value for CVar should be specified at singe time")

		self._default = default
		self._default_factory = default_factory
		self._processors = processors
		self._validators = validators
		self._raw_default = raw_default
		self._name = "" # will be set after __init__ in __set_name__ if in class
		# For check value cache is valid
		self._cached_raw: Any | None = None
		self._cached_value: _T | None = None

	def __set_name__(self, owner: type, name: str):
		if not issubclass(owner, _BaseConfig):
			raise TypeError("CVar-s can be defined only in Config class")
		self._name = name
		self._config_cls: type[_BaseConfig] = owner

	def __str__(self):
		assert len(self._name) > 0
		return self._name

	def _get_info(self) -> _CVarInfo:
		return _CVarInfo(name=self._name)

	def _process_raw(self, raw: Any) -> _T:
		value = raw
		for process in self._processors:
			value = process(value, self._get_info())
		return cast(_T, value)

	def _validate_value(self, value: _T) -> None:
		for validate in self._validators:
			validate(value, self._get_info())

	def _get_default_value(self) -> _T:
		if self._default is not UNSET:
			assert self._raw_default is None
			assert self._default_factory is None
			return self._default

		if self._default_factory is not None:
			assert self._default is None
			assert self._raw_default is None
			return self._default_factory()

		assert self._default is None
		assert self._default_factory is None
		return self._process_raw(self._raw_default)

	def _is_cache_valid(self, raw: Any) -> bool:
		if (self._cached_raw is None):
			return False

		# If eq operator is not overridden cache always invalid
		if type(self._cached_raw).__eq__ == object.__eq__:
			return False

		return self._cached_raw is not None and self._cached_raw == raw

	def _get_value(self) -> _T:
		self._cached_raw = raw = _get_config_dict().get(self._name, UNSET)
		if raw is UNSET:
			self._cached_value = self._get_default_value()
			return self._cached_value

		if self._is_cache_valid(raw):
			assert self._cached_value is not None
			return self._cached_value

		value = self._process_raw(raw)
		self._validate_value(value)
		self._cached_value = value
		return value

	@overload
	def __get__(self, instance: None, owner: type) -> Self: ...
	@overload
	def __get__(self, instance: object, owner: type) -> _T: ...
	def __get__(self, instance: object | None, owner: type) -> Self | _T:
		if instance is None:
			return self
		return self._get_value()

	def __set__(self, instance: object, value: Any) -> NoReturn:
		raise AttributeError("CVar-s can't be set from instance")


# Special errors for processors & validators
class CVarTypeError(TypeError):
	"""ALLOWED INTERNAL IMPORT"""
	pass

class CVarValueError(ValueError):
	"""ALLOWED INTERNAL IMPORT"""
	pass

# MARK: Processors
def _importable_processor(raw, cvar: _CVarInfo):
	if not isinstance(raw, str):
		raise CVarTypeError(f"{cvar.name} should be a string, got: {typename(raw)}")

	try: return import_string(raw)
	except ImportError as ex:
		raise CVarValueError(f"{cvar.name} should be a dotted module path to object, import is failed. Got: {raw}") \
			from ex

# maybe refactor to processors pipeline?
# - add processors: Sequence[Callable[[Any], Any]]
# - remove default_factory, use raw_default + process_factory
# Example:
# SOME_OPTION: _CVar[Colors] = _CVar(
#     raw_default='some.module.get_default_colors',
#     processors=[
#         import_string_processor,
#         process_factory,
#         DataclassProcessor(Colors),
#     ])

def _importable_factory_processor(raw, cvar: _CVarInfo):
	factory = _importable_processor(raw, cvar)
	if not callable(factory):
		raise CVarTypeError(f"{cvar.name} should be factory (callable), got: {typename(factory)}.")

	return factory()

def _dataclass_processor(dataclass_ref: _TypeRef[_T]):
	def processor(raw, cvar: _CVarInfo):
		base_raw_err_msg = f"{cvar.name} should be Mapping[str, Any]"
		if not isinstance(raw, Mapping):
			raise CVarTypeError(f"{base_raw_err_msg}, got: {typename(raw)}")

		for i, (key, _) in enumerate(raw.items()):
			if not isinstance(key, str): raise CVarTypeError(
				f"{base_raw_err_msg}, got mapping where key type is {typename(key)} (key position is {i})"
			)
		params: Mapping[str, Any] = raw

		dataclass = dataclass_ref.resolve()
		# different (raise/assert): raw specified by user, dataclass specified here, in Config definition
		# reminder for readers: assert does'nt work in production (`python -O`)
		assert isinstance(dataclass, type) and is_dataclass(dataclass)

		return dataclass(**params)
	return processor


# MARK: Validators
@overload
def _validate_is_instance(class_or_tuple_or_callback: type): ...
@overload
def _validate_is_instance(class_or_tuple_or_callback: tuple[type, ...]): ...
@overload
def _validate_is_instance(class_or_tuple_or_callback: Callable[[], type]): ...
@overload
def _validate_is_instance(class_or_tuple_or_callback: Callable[[], tuple[type, ...]]): ...
def _validate_is_instance(class_or_tuple_or_callback: type | tuple[type, ...] | Callable[[], type | tuple[type, ...]]):
	def validator(value: Any, cvar: _CVarInfo):
		class_or_tuple = class_or_tuple_or_callback() if callable(class_or_tuple_or_callback) else class_or_tuple_or_callback
		if isinstance(value, class_or_tuple):
			return

		classes = map(typename, one_or_seq_to_seq(type, class_or_tuple))
		raise CVarTypeError(f"{cvar.name} should be {verb_list(classes)}, got: {typename(value)}")
	return validator

@overload
def _validate_is_subclass(class_or_tuple_or_callback: type): ...
@overload
def _validate_is_subclass(class_or_tuple_or_callback: tuple[type, ...]): ...
@overload
def _validate_is_subclass(class_or_tuple_or_callback: Callable[[], type]): ...
@overload
def _validate_is_subclass(class_or_tuple_or_callback: Callable[[], tuple[type, ...]]): ...
def _validate_is_subclass(class_or_tuple_or_callback: type | tuple[type, ...] | Callable[[], type | tuple[type, ...]]):
	def validator(value: Any, cvar: _CVarInfo):
		_validate_is_instance(type)(value, cvar)
		class_or_tuple = class_or_tuple_or_callback() if callable(class_or_tuple_or_callback) else class_or_tuple_or_callback

		if issubclass(value, class_or_tuple):
			return

		classes = map(typename, one_or_seq_to_seq(type, class_or_tuple))
		raise CVarTypeError(f"{cvar.name} should be subclass of {verb_list(classes)}, got: {typename(value)}")
	return validator

def _validate_value_in(enum: IterableAbstractSet[_T]):
	def validator(value, cvar: _CVarInfo):
		if value not in enum:
			raise CVarValueError(f"{cvar.name} should be in {{{', '.join(map(str, enum))}}}, got: {value}")
	return validator


# MARK: Config def
# Maybe add to Config constructor required arg Mapping[str, Any]?
# And use them in CVar instead hardcoded _CONFIG_DICT in _get_value.
# This add abillity to local overrides.

# Example:
# here:
# > config = Config(_CONFIG_DICT) // global
# in some admin.py:
# > registrar = AdminRegistrar(
# >     config = Config({
# >         **conf.get_config_dict(),
# >         'DEFAULT_ADMINS_RESOLVER': 'src.orders.admin.resolvers.DefaultAdminsResolverForOrders'
# >     })
# > )

# But.. hmm...
# I wants to see local overrides like that:
# > registrar = AdminRegistrar(
# >     config = Config({
# >         **conf.get_config_dict(),
# >         Config.DEFAULT_ADMINS_RESOLVER: DefaultAdminsResolverForOrders
# >     })
# > )
# need to think about it.
_RegisteringLogColorsTypeRef = _TypeRef["RegisteringLogColors"]('admin_registrar.dataclasses.RegisteringLogColors')
class Config(_BaseConfig):
	ADMINS_FOR_MODELS: _CVar[Any] = _CVar(
		raw_default='admin_registrar.internal.conf_defaults.get_default_admins_for_models',
		processors=[_importable_factory_processor],
		validators=[])
	"""Default admins for models. Named just "Admins for models" for shorter name"""
	DEFAULT_ADMINS_RESOLVER: _CVar[DefaultAdminsResolver] = _CVar(
		raw_default='admin_registrar.internal.conf_defaults.DEFAULT_RESOLVER',
		processors=[_importable_processor],
		validators=[_validate_is_instance(DefaultAdminsResolver)])
	HIDDEN_ADMIN_CLASS: _CVar[type[ModelAdmin]] = _CVar(
		raw_default='admin_registrar.admin.HiddenAdmin',
		processors=[_importable_processor],
		validators=[_validate_is_subclass(ModelAdmin)])
	ENABLE_COLORED_LOGS: _CVar[bool] = _CVar(
		default=True,
		validators=[_validate_is_instance(bool)])
	REGISTERING_LOG_COLORS: _CVar["RegisteringLogColors"] = _CVar(
		raw_default={},
		processors=[_dataclass_processor(_RegisteringLogColorsTypeRef)],
		validators=[_validate_is_instance(_RegisteringLogColorsTypeRef.resolve)])
	REGISTERING_LOG_LEVEL: _CVar[int] = _CVar(
		# factory way used because django_settings.DEBUG overrided in some context
		# and conf.py can be imported before this override
		default_factory=lambda: logging.DEBUG if django_settings.DEBUG else logging.INFO,
		validators=[_validate_is_instance(int)])
	ADMIN_REGISTRY: _CVar[AdminRegistry] = _CVar(
		default=django.contrib.admin.site,
		validators=[_validate_is_instance(AdminRegistry)])

# MARK: Public API
# Temporary private
# Needs for feature described at Config def
def __get_config_dict() -> dict[str, Any]:
	"""Returns deep copy of used config dict"""
	return deepcopy(_get_config_dict())

config = Config()
