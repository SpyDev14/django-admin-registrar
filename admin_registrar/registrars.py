from logging 	import getLogger
from typing 	import Iterable

from django.contrib.admin 	import ModelAdmin, options, site
from django.db.models 		import Model
from django.apps 			import AppConfig, apps

from admin_registrar._utils.colors 	import Fore
from admin_registrar._utils 		import typename
from admin_registrar.resolvers		import DefaultAdminsResolver
from admin_registrar.conf 			import settings


_logger = getLogger(__name__)

class AdminRegistrar:
	def __init__(self,
			app: type[AppConfig],
			*,
			admins_for_models: 	dict[type[Model], type[ModelAdmin]] | None = None,
			excluded_models: 	set[type[Model]] | None = None,
			hidden_models: 		set[type[Model]] | None = None,

			default_admins_resolver: DefaultAdminsResolver = settings.DEFAULT_ADMINS_RESOLVER,
		):
		self._app = app
		self._excluded_models 	= excluded_models or set()
		self._hidden_models 	= hidden_models or set()
		self._admins_for_models = admins_for_models or dict()

		self._resolve_default_admin_for = default_admins_resolver

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
		self.exclude(inline.model)
		return inline

	def set_admin_class_for_model(self, model: type[Model], admin_class: type[ModelAdmin]):
		"""
		Set defined admin class for given model.

		Example
		---
		```
		registrar.set_admin_class_for_model(Product, ProductAdmin)
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

		Use `registrar.set_admin_class_for_model(Product, ProductAdmin)`
		instead for better readabillity.
		"""
		def decorator(admin_class: type[ModelAdmin]):
			self.set_admin_class_for_model(model, admin_class)
			return admin_class
		return decorator

	def hide_model(self, model_class: type[Model]):
		"""
		Регистрирует модель в админ-панели под специальным админ-классом, который
		отключает её отображение на странице админ-панлеи, но добавляет API эндпоинты
		для взаимодействия с ней.

		Примеры использования:
		- Нужна возможность создавать и управлять моделью через форму **другой** модели, не
		  добавляя модель в общий список моделей в админ-панели.
		- Нужно добавить `autocomplete_fields` (модель с autocomplete должна быть
		  зарегистрированна с настроенным search), или что-то похожее в форме **другой** модели,
		  но без отображения **этой** модели в общем списке в админ-панели.
		"""
		self._hidden_models.add(model_class)

	def _register(self, model_class: type[Model], admin_class: type[ModelAdmin]) -> None:
		site.register(model_class, admin_class)

	def _resolve_admin_for(self, model_class: type[Model]) -> type[ModelAdmin]:
		if model_class in self._hidden_models:
			return settings.HIDDEN_ADMIN_CLASS

		return (
			self._admins_for_models.get(model_class)
			or self._resolve_default_admin_for(model_class)
		)

	def _make_log_message(self, model_class: type[Model], admin_class: type[ModelAdmin] | None) -> str:
		START_LOG_TEXT = (
			f"model {Fore.L_GREEN}{typename(model_class)}{Fore.RESET} "
			f"from {Fore.L_MAGENTA}{self._app.name}{Fore.RESET}"
		)

		if admin_class is None:
			assert model_class in self._excluded_models
			return f"{START_LOG_TEXT} is {Fore.L_RED}excluded{Fore.RESET}."

		middle_log_text = (
			"was hidden by" if model_class in self._hidden_models
			else "succesful registered with"
		)

		return f"{START_LOG_TEXT} {middle_log_text} {Fore.L_GREEN}{typename(admin_class)}{Fore.RESET} admin class."

	def peform_register(self):
		if self._registration_performed:
			_logger.error(f'An attempt to re-register for {self._app.name} app.')
			return

		_logger.debug(f'-- Start {Fore.L_MAGENTA}{self._app.name}{Fore.RESET} registration -------')
		for model_class in apps.get_app_config(self._app.name).get_models():
			if model_class in self._excluded_models:
				_logger.debug(self._make_log_message(model_class, None))
				continue

			admin_class = self._resolve_admin_for(model_class)

			self._register(model_class, admin_class)
			_logger.debug(self._make_log_message(model_class, admin_class))

		self._registration_performed = True
