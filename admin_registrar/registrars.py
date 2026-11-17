from functools import wraps
from typing import Iterable, Iterator, Literal, MutableMapping, MutableSet, TypeVar
import logging

from django.contrib.admin import ModelAdmin, options
from django.db.models import Model
from django.apps import AppConfig, apps

from admin_registrar.internal import typename, deprecated
from admin_registrar.utils.colors import Fore
from admin_registrar.conf import config as global_conf, Config


_logger = logging.getLogger(__name__)
_TInline = TypeVar('_TInline', bound=type[options.InlineModelAdmin])

# Reminder: prefix "_" means protected access mode, override by subclasses
# is allowed
class AdminRegistrar:
	def __init__(self,
			app: type[AppConfig],
			*,
			admins_for_models: MutableMapping[type[Model], type[ModelAdmin]] | None = None,
			excluded_models:   MutableSet[type[Model]] | None = None,
			hidden_models:     MutableSet[type[Model]] | None = None,

			config: Config | None = None
		):
		# `or` return right if left is False. Empty dict and other stuff with
		# defined __bool__ can be ignored, so i write this
		# Was add when any used conf var was dublicated here to self vars
		def _(a, b): return a if a is not None else b

		self._app_class = app
		self._excluded_models   = _(excluded_models,   set())
		self._hidden_models     = _(hidden_models,     set())
		self._admins_for_models = _(admins_for_models, dict())

		self._conf = _(config, global_conf)

		self._registration_performed: bool = False
		self._registration_is_deferred: bool = False

	def exclude(self, model: type[Model]):
		"""
		Exclude model from models to registration.

		Example
		-------
		```python
		registrar.exclude(SomeModel)
		```
		"""
		self._excluded_models.add(model)

	def exclude_several(self, models: Iterable[type[Model]]):
		"""
		Exclude several models from models to registration.

		Example
		-------
		```python
		registrar.exclude_several([
			SomeModelOne,
			SomeModelTwo,
		])
		```
		"""
		for model in models:
			self.exclude(model)

	def exclude_inline(self, inline: _TInline) -> _TInline:
		"""
		Exclude model who used in given inline.

		Example
		-------
		```python
		@registrar.exclude_inline
		class ProductImageInline(TabularInline):
			model = ProductImage
		# instead
		registrar.exclude(ProductImage)
		```
		"""
		self.exclude(inline.model) # type: ignore // model is class var, but not annotated as it
		return inline

	def set_admin_for_model(self, model: type[Model], admin_class: type[ModelAdmin]):
		"""
		Set defined admin class for given model.

		Example
		-------
		```
		registrar.set_admin_for_model(Product, ProductAdmin)
		```

		Exists for excluding something like this:
		```
		registrar.set_for_model(Product)(ProductAdmin)
		```
		"""
		self._admins_for_models[model] = admin_class

	def set_for_model(self, model: type[Model]):
		"""
		Set defined admin class for given model with decorator syntax.

		Example
		-------
		```
		@registrar.set_for_model(Product)
		class ProductAdmin(ModelAdmin):
			...
		```

		Please, do not use this method for this:
		```
		registrar.set_for_model(Product)(ProductAdmin)
		```

		Use `registrar.set_admin_for_model(Product, ProductAdmin)`
		instead for better readability.
		"""
		def decorator(admin_class: type[ModelAdmin]):
			self.set_admin_for_model(model, admin_class)
			return admin_class
		return decorator

	def hide(self, model: type[Model]):
		"""
		### [En] (has russian below)
		<hr>

		Registers the model in the admin panel under `HiddenAdmin` (by default).
		This is a special admin class that allows you to register the model in
		the admin panel but not display it in the general list (on the left in
		the standard panel).

		This can be useful when you have a small auxiliary model for another model,
		for example, "Product Image", "Product Characteristic Type", "Article Tag"
		(or category; a model with only a name field and a foreign key to the article).
		You don't want to clutter the general list with these micro‑models, but you
		need the ability to create/change/delete records of these models through the
		admin in the main model's form (interaction buttons next to the selection field).

		The standard `HiddenAdmin` from this package allows you to access the list
		page via the following path: <div>
			`Form with a field for the hidden model => Change => Save => List of
			hidden model records`.
		</div>

		You can override the admin class used in the package settings.

		This is to some extent non‑standard functionality. Share your opinion about
		this feature on the <a href="https://github.com/SpyDev14/django-admin-registrar">package's GitHub</a>.
		Thank you.

		### [Ru]
		<hr>

		Регистрирует модель в админ-панели под `HiddenAdmin` (по умолчанию).
		Это специальный админ-класс, который позволяет зарегистрировать модель
		в админ-панели, но не отображать её в общем списке (слева в стандартной
		панели).

		Это может понадобится тогда, когда у вас есть маленькая вспомогательная модель
		для другой модели, например "Изображение товара", "Тип характеристики товара",
		"Тег статьи" (или категория; модель с одним только name полем и fk на статью)
		и вы не хотите загромождать общий список этими микро-моделями, но вам нужна
		возможность создавать / изменять / удалять записи этих моделей через админку
		в форме основной модели (кнопки взаимодействия рядом с полем выбора).

		Стандартный `HiddenAdmin` из этого пакета позволяет попасть на страницу списка
		следущим путём: `Форма с полем на скрытую модель => Изменить => Сохранить =>
		Список записей скрытой моделей`.

		Вы можете переопределить используемый админ-класс в настройках пакета.

		Это в определённой мере нестандартная функциональность. Поделитесь своим
		мнением по поводу этой функции на
		<a href="https://github.com/SpyDev14/django-admin-registrar">github пакета</a>.
		Спасибо.
		"""
		self._hidden_models.add(model)

	def hide_several(self, models: Iterable[type[Model]]):
		"""`hide` all given models"""
		for model in models:
			self.hide(model)

	def _register_on_site(self, model: type[Model], admin_class: type[ModelAdmin]) -> None:
		self._conf.ADMIN_REGISTRY.register(model, admin_class)

	def _is_model_registered(self, model: type[Model]) -> bool:
		return self._conf.ADMIN_REGISTRY.is_registered(model)

	def _try_register_on_site(self, model: type[Model], admin_class: type[ModelAdmin]) -> None:
		if self._is_model_registered(model):
			AR_COLOR = self._conf.REGISTERING_LOG_COLORS.already_registered
			M_COLOR = self._conf.REGISTERING_LOG_COLORS.model
			APP_COLOR = self._conf.REGISTERING_LOG_COLORS.app
			ADMIN_COLOR = self._conf.REGISTERING_LOG_COLORS.admin_class
			_logger.warning(
				f"Model {M_COLOR}{typename(model)}{Fore.RESET} from {APP_COLOR}{model._meta.app_label}{Fore.RESET} "
				f"{AR_COLOR}already registered.{Fore.RESET} Automatic registration by {ADMIN_COLOR}{typename(admin_class)} "
				f"{Fore.RESET} admin class skipped."
			)
			return

		self._register_on_site(model, admin_class)
		self._log_registering(
			self._make_log_message(model, was="hidden")
			if model in self._hidden_models
			else self._make_log_message(model, admin_class=admin_class)
		)

	def _resolve_default_admin_for(self, model: type[Model]) -> type[ModelAdmin]:
		return self._conf.DEFAULT_ADMINS_RESOLVER(model, self._conf.ADMINS_FOR_MODELS)

	def _resolve_admin_for(self, model: type[Model]) -> type[ModelAdmin]:
		if model in self._hidden_models:
			return self._conf.HIDDEN_ADMIN_CLASS

		return (
			self._admins_for_models.get(model)
			or self._resolve_default_admin_for(model)
		)

	def _make_log_message(self,
		model: type[Model],
		*,
		admin_class: type[ModelAdmin] | None = None,
		was: Literal["excluded", "hidden"] | None = None
	) -> str:
		assert (admin_class is None) != (was is None)
		assert was in { "excluded", "hidden", None }

		MODEL_COLOR     = self._conf.REGISTERING_LOG_COLORS.model
		APP_COLOR       = self._conf.REGISTERING_LOG_COLORS.app
		EXCLUDED_COLOR  = self._conf.REGISTERING_LOG_COLORS.excluded
		ADMIN_COLOR     = self._conf.REGISTERING_LOG_COLORS.admin_class

		start_text = (
			f"model {MODEL_COLOR}{typename(model)}{Fore.RESET} "
			f"from {APP_COLOR}{self._app_class.name}{Fore.RESET}"
		)

		if was == "excluded":
			return f"{start_text} is {EXCLUDED_COLOR}excluded{Fore.RESET}."

		middle_text = (
			"was hidden by" if was == "hidden"
			else "successful registered by"
		)

		return f"{start_text} {middle_text} {ADMIN_COLOR}{typename(admin_class)}{Fore.RESET} admin class."

	def _get_models_to_register(self) -> Iterator[type[Model]]:
		app_class = self._app_class
		label = getattr(app_class, "label", None) or app_class.name.rpartition(".")[2]
		return apps.get_app_config(label).get_models()

	def _log_registering(self, msg: object) -> None:
		_logger.log(self._conf.REGISTERING_LOG_LEVEL, msg)

	def register(self):
		if self._registration_performed:
			raise RuntimeError(
				f'An attempt to re-register admins by AdminRegistrar '
				f'for {self._app_class.name} app.'
			)

		self._log_registering(
			f'\n-- Start {self._conf.REGISTERING_LOG_COLORS.app}'
			f'{self._app_class.name}{Fore.RESET} registration -------'
		)

		for model_class in self._get_models_to_register():
			if model_class in self._excluded_models:
				self._log_registering(self._make_log_message(model_class, was="excluded"))
				continue

			admin_class = self._resolve_admin_for(model_class)

			self._try_register_on_site(model_class, admin_class)

		self._registration_performed = True

	# 1. fix type (`{peform -> perform}_registering`)
	# 2. change to better name (just "register" instead "perform_registering")
	@deprecated("Use register instead. Will be removed in v1.0.0")
	def peform_register(self): self.register()

	def defer_registration(self):
		"""
		Defer registration to given app `ready`.

		Use when you define admin classes at several modules.

		Given app class `ready` method will be overridden to special,
		wrapper.

		This registrar `register` will be called **after** original `ready`.

		Ps: Previously this had to be done manually.
		"""
		if self._registration_is_deferred:
			raise RuntimeError(
				f'An attempt to double defer registration admins by '
				f'AdminRegistrar for {self._app_class.name} app.'
			)

		original_ready = self._app_class.ready
		registrar = self

		@wraps(original_ready)
		def new_ready(self: AppConfig): # name `self` is required for type matching
			original_ready(self)
			registrar.register()

		self._app_class.ready = new_ready
		self._registration_is_deferred = True
