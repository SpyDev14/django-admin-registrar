from dataclasses 	import dataclass
from typing 		import Iterable, Iterator
import logging

from django.contrib.admin 	import ModelAdmin, options, site
from django.db.models 		import Model
from django.apps 			import AppConfig, apps

from admin_registrar.utils.colors 	import Fore
from admin_registrar.utils 			import typename
from admin_registrar.resolvers		import DefaultAdminsResolver
from admin_registrar.conf 			import settings


_logger = logging.getLogger(__name__)

@dataclass
class RegisteringLogColors:
	model: str
	admin_class: str
	app: str
	excluded: str

class AdminRegistrar:
	def __init__(self,
			app: type[AppConfig],
			*,
			admins_for_models: 	dict[type[Model], type[ModelAdmin]] | None = None,
			excluded_models: 	set[type[Model]] | None = None,
			hidden_models: 		set[type[Model]] | None = None,

			default_admins_resolver: DefaultAdminsResolver = settings.DEFAULT_ADMINS_RESOLVER,
			registering_log_level: int = logging.DEBUG,
			registering_log_colors: RegisteringLogColors | None = None,
		):
		self._app = app
		self._excluded_models 	= excluded_models or set()
		self._hidden_models 	= hidden_models or set()
		self._admins_for_models = admins_for_models or dict()

		self._default_admins_resolver = default_admins_resolver
		self._registering_log_level = registering_log_level
		self._registering_log_colors = registering_log_colors or RegisteringLogColors(
			model=Fore.L_GREEN,
			admin_class=Fore.L_GREEN,
			app=Fore.L_MAGENTA,
			excluded=Fore.RED,
		)

		self._registration_performed: bool = False

	def exclude(self, model: type[Model]):
		"""
		Exclude model from to registration list.

		Example
		---
		```python
		registrar.exclude(SomeModel)
		```
		"""
		self._excluded_models.add(model)

	def exclude_several(self, models: Iterable[type[Model]]):
		"""
		Exclude several models from to registration list.

		Example
		---
		```python
		registrar.exclude_several([
			SomeModelOne,
			SomeModelTwo,
		])
		```
		"""
		self._excluded_models.update(models)

	def exclude_inline(self, inline: type[options.InlineModelAdmin]):
		"""
		Exclude model who used in given inline.

		Example
		---
		```python
		@registrar.exclude_inline
		class ProductImageInline(TabularInline):
			model = ProductImage
		# Or so
		registrar.exclude_inline(ProductImageInline)
		```
		"""
		self.exclude(inline.model) # type: ignore // model is ClassVar, but not annotated as it
		return inline

	def set_admin_for_model(self, model: type[Model], admin_class: type[ModelAdmin]):
		"""
		Set defined admin class for given model.

		Example
		---
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
		---
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
		instead for better readabillity.
		"""
		def decorator(admin_class: type[ModelAdmin]):
			self.set_admin_for_model(model, admin_class)
			return admin_class
		return decorator

	def hide(self, model: type[Model]):
		"""
		### [En] (Has Ru language below)
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
		"""Performs `hide` for all given models."""
		self._hidden_models.update(models)

	def _register_on_site(self, model: type[Model], admin_class: type[ModelAdmin]) -> None:
		site.register(model, admin_class)

	def _resolve_default_admin_for(self, model: type[Model]) -> type[ModelAdmin]:
		return self._default_admins_resolver(model)

	def _resolve_admin_for(self, model: type[Model]) -> type[ModelAdmin]:
		if model in self._hidden_models:
			return settings.HIDDEN_ADMIN_CLASS

		return (
			self._admins_for_models.get(model)
			or self._resolve_default_admin_for(model)
		)

	def _make_log_message(self, model: type[Model], admin_class: type[ModelAdmin] | None) -> str:
		MODEL_COLOR 	= self._registering_log_colors.model
		APP_COLOR 		= self._registering_log_colors.app
		EXCLUDED_COLOR 	= self._registering_log_colors.excluded
		ADMIN_COLOR 	= self._registering_log_colors.admin_class

		START_LOG_TEXT = (
			f"model {MODEL_COLOR}{typename(model)}{Fore.RESET} "
			f"from {APP_COLOR}{self._app.name}{Fore.RESET}"
		)

		if admin_class is None:
			assert model in self._excluded_models
			return f"{START_LOG_TEXT} is {EXCLUDED_COLOR}excluded{Fore.RESET}."

		middle_log_text = (
			"was hidden by" if model in self._hidden_models
			else "succesful registered with"
		)

		return f"{START_LOG_TEXT} {middle_log_text} {ADMIN_COLOR}{typename(admin_class)}{Fore.RESET} admin class."

	def _get_models_to_register(self) -> Iterator[type[Model]]:
		return apps.get_app_config(self._app.name).get_models()

	def _log_registering(self, msg: object) -> None:
		_logger.log(self._registering_log_level, msg)

	def peform_register(self):
		if self._registration_performed:
			_logger.error(f'An attempt to re-register for {self._app.name} app.')
			return

		self._log_registering(f'-- Start {self._registering_log_colors.app}{self._app.name}{Fore.RESET} registration -------')
		for model_class in self._get_models_to_register():
			if model_class in self._excluded_models:
				self._log_registering(self._make_log_message(model_class, None))
				continue

			admin_class = self._resolve_admin_for(model_class)

			self._register_on_site(model_class, admin_class)
			self._log_registering(self._make_log_message(model_class, admin_class))

		self._registration_performed = True
