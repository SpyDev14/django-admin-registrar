from importlib	import import_module
from logging 	import getLogger

from django.contrib.admin 	import ModelAdmin, site, options
from django.db.models 		import Model
from django.conf 			import settings
from django.apps 			import apps

from colorama import Fore, Style

from admin_registrator.utils import typename


_logger = getLogger(__name__)

# Задавать в DEFAULT_MODEL_ADMIN_CLASSES в настройках, подробнее
# в документации AdminModelRegister.
# Ps: если указать Model: CustomModelAdmin - это сработает.
_default_admin_classes_for_models: dict[type[Model], type[ModelAdmin]] = { }
_defaults_loaded: bool = False
_hidden_admin_class: type[ModelAdmin] | None = None


def _get_default_admin_class_for_model(model_class: type[Model]) -> type[ModelAdmin] | None:
	for cls in model_class.mro():
		if not issubclass(cls, Model):
			break
		if cls in _default_admin_classes_for_models:
			return _default_admin_classes_for_models[cls]

	return None


def _set_default_admin_class_for_model_subclasses(model_class: type[Model], admin_class: type[ModelAdmin]):
	"""
	Устанавливает переданный подкласс `ModelAdmin` для подклассов
	указанной модели как admin class по умолчанию.

	Raises:
		TypeError:
			- Класс модели не является подклассом `Model`
			- Admin class не является подклассом `ModelAdmin`
		RuntimeError:
			- Уже зарегистрированно
	"""
	if not issubclass(model_class, Model):
		raise TypeError("Model class shoud be a subclass of Model")

	if not issubclass(admin_class, ModelAdmin):
		raise TypeError("Model admin class shoud be a subclass of ModelAdmin")

	if model_class in _default_admin_classes_for_models:
		# Для явности. Если нужно будет переопределять - сделаю отдельный метод.
		raise RuntimeError("Already registered")

	_default_admin_classes_for_models[model_class] = admin_class
	_logger.debug(
		f"admin class {L_GREEN}{admin_class.__qualname__}{RESET} succesfully setted "
		f"as default admin class for subclasses of {L_GREEN}{typename(model_class)}{RESET}."
	)


def _load_default_admin_classes_for_models():
	"""
	Загружает стандартные админ-классы для моделей из настроек
	проекта, из поля `DEFAULT_MODEL_ADMIN_CLASSES`.

	### Пример использования:
	- **settings.py**
	```
	DEFAULT_MODEL_ADMIN_CLASSES = {
		'solo.models.SingletonModel': 'solo.admin.SingletonModelAdmin'
	}
	```
	Теперь все `SingletonModel` в админке по умолчанию будут
	регистрироваться под `SingletonModelAdmin`.

	Raises:
		RuntimeError:
			- Уже загружено (повторный вызов)
	"""
	global _defaults_loaded
	if _defaults_loaded:
		raise RuntimeError('Already loaded')

	mapping: dict[str, str] = getattr(settings, 'DEFAULT_MODEL_ADMIN_CLASSES', {})

	for model_path, admin_path in mapping.items():
		# 'solo.models.SingletonModel' -> 'solo.models', 'SingletonModel'
		model_module, model_class_name = model_path.rsplit('.', 1)
		admin_module, admin_class_name = admin_path.rsplit('.', 1)

		_set_default_admin_class_for_model_subclasses(
			model_class = getattr(import_module(model_module), model_class_name),
			admin_class = getattr(import_module(admin_module), admin_class_name)
		)

	_defaults_loaded = True

# TODO: Вынести в отдельный Python пакет
# TODO: Добавить hide_model в документацию
# TODO: Добавить exclude_inline_model в документацию
# TODO: Убрать exclude_models из документации
# TODO: Добавить в документацию, как использовать при регистрации через несколько файлов
# 	admin/
# 		__init__.py:
# 			| registrator = AdminRegistrator()
# 			| from .general import * # <- Импорт для инициализации модулей
# 		general.py:
# 			| from . import registrator
# 			| @registrator.set_for_model(...)
# 			| class ...(...): ...
# 	apps.py:
# 		| class ...Config(...):
# 		|     def ready(self):
# 		|         from admin import registrator
# 		|         registrator.register()
# TODO: Добавить проверки, что модели уже где-то не зарегистрированы
# TODO: Добавить поддержку множественного наследования в resolver админ-класса по умолчанию
# TODO: Сделать resolver подменяемым, resolver по умолчанию задавать через настройки,
# добавить его в аргументы конструктора для возможности локальной подмены.
# (не скрытая ли, не исключена ли, не зарегистрирована ли в Django)
# NOTE: Переименовать переменную custom_admin_classes_for_models и связанные с ней методы?
# NOTE: Мб. добавить инструментарий для регистрации по умолчанию с параметрами?
# Например, register_with(model, params: dict) (.register_with(MyModel, dict(inlines = [MyModelImageInline])))
# где MyModel - Ordered & BR Model с OrderedBaseRenderableModelAdmin
class AdminRegistrator:
	"""
	`AdminRegistrator` нужен для удобной автоматической регистрации моделей
	в Django-админке.

	<small><b>Админ-класс</b> - это класс, наследующийся от <code>ModelAdmin</code>, используемый
	для отображения модели в админ-панели.</small>
	<hr>

	Используйте `exclude_model` для исключения модели из списка для регистрации, либо
	`exclude_models` для множественного исключения.
	<hr>

	Используйте `set_custom_admin_class_for_model()` для установки кастомного админ-класса
	для конкретной модели, либо используйте версию-декоратор: `@set_for_model()`
	над кастомным админ-классом.
	<hr>

	**После определения моделей для регистрации и их админ-классов вызовите `register()`
	для произведения регистрации.**
	<hr>

	Добавьте в **settings.py** словарь (`dict`) с названием `DEFAULT_MODEL_ADMIN_CLASSES`
	с парами ключ-значение вида: `'$модуль.КлассМодели': '$модуль.АдминКласс'` чтобы задать
	админ-классы по умолчанию для указанных моделей и их подклассов (пример ниже).
	<hr>

	### Пример использования:
	- **settings.py**
	```
	DEFAULT_MODEL_ADMIN_CLASSES = {
		'solo.models.SingletonModel': 'solo.admin.SingletonModelAdmin'
	}
	```

	- **models.py**
	```
	class MyModel(Model): ...
	class MySpecialModel(Model): ...
	class MyModelForExclude(Model): ...
	class MyModelForExcludeAlt(Model): ...
	class MySingletonModel(SingletonModel): ...
	```

	- **admin.py**
	```
	registrator = AdminRegistrator(
		app_name = MyAppConfig.name,
		# Рекомендуемый способ для исключения моделей
		exclude_models = {MyModelForExclude},
	)

	# Допустим, получили от куда-то из вне
	collected_models_for_exclude = {models.MyModelForExcludeAlt}
	registrator.exclude_models(collected_models_for_exclude)

	# Делаем что-то и поэтому нужно исключить конкретно эту модель
	registrator.exclude_model()
	class MySpecialModelInline(StackedInline):
		...

	# Нужна кастомная ModelAdmin
	@registrator.set_for_model(models.MyModel)
	class MyModelAdmin(ModelAdmin):
		inlines = [MySpecialModelInline]

	# Проводим регистрацию всех моделей из приложения MyApp
	# с учётом всех настроек
	registrator.register()
	```

	Теперь в нашей админке будут зарегистрированны все модели из приложения
	`my_app`, кроме `MyModelForExclude`, `MyModelForExcludeAlt` и `MySpecialModel`.
	`MyModel` будет зарегистрированна под `MyModelAdmin`, а `MySingletonModel`
	будет зарегистрированна под `SingletonModelAdmin`.
	"""
	def __init__(self,
			*,
			app_name: str,
			excluded_models: set[type[Model]] = set(),
			custom_admin_classes_for_models: \
				dict[type[Model], type[ModelAdmin]] = dict()):
		"""
		Документацию об использовании смотрите в документации самого класса
		(это документация конструктора)
		Params:
			app_name:
				Название приложения, с которым будет вестись работа.
				Указывайте название приложения в котором вы регистрируете модели.
				Рекомендуется делать это через `AppConfig.name`, вместо прямого
				указания названия.

			excluded_models:
				Исключённые из списка регистрации модели по умолчанию.

			custom_admin_classes_for_models:
				Кастомные `ModelAdmin` для конкретных моделей по умолчанию.
		"""
		self._app_name = app_name
		self._excluded_models = excluded_models
		self._custom_admin_classes_for_models = custom_admin_classes_for_models

		if not _defaults_loaded:
			_load_default_admin_classes_for_models()

	def exclude_model(self, model: type[Model]):
		"""Исключит модель из списка для регистрации."""
		self._excluded_models.add(model)

	def exclude_inline_model(self, inline_class: type[options.InlineModelAdmin]):
		"""Исключит модель инлайна из списка для регистриции"""
		self.exclude_model(inline_class.model)

	def set_custom_admin_class_for_model(self, model: type[Model], admin_class: type[ModelAdmin]):
		"""Установит кастомную `ModelAdmin` для указанной модели."""
		self._custom_admin_classes_for_models[model] = admin_class

	def set_for_model(self, model: type[Model]):
		"""Установит класс ниже в качестве кастомной `ModelAdmin`
		для указанной модели."""
		def decorator(admin_class: type[ModelAdmin]):
			self.set_custom_admin_class_for_model(model, admin_class)
			return admin_class

		return decorator

	# TODO: Реализовать hide_model по нормальному
	# - Отдельную переменную для отметки моделей как скрытых
	# - Регистрировать под HiddenModel в методе регистрации
	__default_hidden_admin_class: type[ModelAdmin] | None = None
	def hide_model(self, model: type[Model]):
		cls = type(self)
		if not cls.__default_hidden_admin_class:
			cls.__default_hidden_admin_class = type(
				'HiddenAdmin', (ModelAdmin, ),
				{'get_model_perms': lambda *_: {}}
			)

		# Тут отдельную переменную
		self.set_custom_admin_class_for_model(
			model, (_hidden_admin_class or cls.__default_hidden_admin_class)
		)


	def register(self):
		"""
		Используйте для проведения регистрации моделей в самом конце модуля.
		Выбросит стандартное исключение о попытке повторной регистрации модели,
		если вы пытались зарегистрировать что-то вручную через `admin.site.register()`.

		Если вам действительно необходимо регистрировать какую-то модель вручную -
		пометьте её как исключённую из списка для регистрации.
		"""
		_logger.debug('-' * 48)
		for model in apps.get_app_config(self._app_name).get_models():
			START_LOG_TEXT = (
				f"model {Style.BRIGHT}{Fore.GREEN}{typename(model)}{Style.RESET_ALL} "
				f"from {Style.BRIGHT}{Fore.MAGENTA}{self._app_name}{Style.RESET_ALL}"
			)
			if model in self._excluded_models:
				_logger.debug(f"{START_LOG_TEXT} is {Style.BRIGHT}{Fore.RED}excluded{Style.RESET_ALL}.")
				continue

			admin_class = ModelAdmin

			if model in self._custom_admin_classes_for_models:
				admin_class = self._custom_admin_classes_for_models[model]

			elif default_admin_class := _get_default_admin_class_for_model(model):
				admin_class = default_admin_class

			site.register(model, admin_class)
			_logger.debug(
				f"{START_LOG_TEXT} succesful registered with {Style.BRIGHT}{Fore.GREEN}{typename(admin_class)}{Style.RESET_ALL} admin class."
			)
