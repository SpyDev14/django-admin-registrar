from logging 	import getLogger
from typing 	import Callable, Iterable

from django.contrib.admin 	import ModelAdmin, site, options
from django.db.models 		import Model
from django.apps 			import AppConfig

from admin_registrar.resolvers	import AdminsResolver, first_mro_match_resolver
from admin_registrar._utils 	import typename
from admin_registrar.conf 		import admin_reg_settings


L_GREEN = ""
L_RED = ""
L_MAGENTA = ""
RESET = ""

_logger = getLogger(__name__)

if admin_reg_settings.COLORED_LOGS:
	try:
		from colorama import Fore, Style, init
		init()
		L_GREEN = f"{Style.BRIGHT}{Fore.GREEN}"
		L_RED = f"{Style.BRIGHT}{Fore.RED}"
		L_MAGENTA = f"{Style.BRIGHT}{Fore.MAGENTA}"
		RESET = Style.RESET_ALL
	except ImportError:
		_logger.error(f"The COLORED_LOGS parameter has been set, but you do not have the 'colorama' package installed.")

class AdminRegistrar:
	def __init__(self,
			app: AppConfig,
			*,
			classes_for_models: dict[type[Model], type[ModelAdmin]] | None = None,
			excluded_models: 	set[type[Model]] | None = None,
			hidden_models: 		set[type[Model]] | None = None,

			admins_resolver: AdminsResolver \
				= admin_reg_settings.DEFAULT_ADMINS_RESOLVER,
		):
		self._app = app
		self._excluded_models 	= excluded_models or set()
		self._hidden_models 	= hidden_models or set()
		self._admin_classes_for_models = classes_for_models or dict()
		self._admins_resolver = admins_resolver

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
		Exclude model who used in this inline.
		Works with decorator syntax

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
		self._admin_classes_for_models[model] = admin_class

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
		self._hidden_models.add(model_class)

	def peform_register(self):
		_logger.debug('-' * 48)
		for model in self._app.get_models():
			START_LOG_TEXT = (
				f"model {L_GREEN}{typename(model)}{RESET} "
				f"from {L_MAGENTA}{self._app.name}{RESET}"
			)

			if model in self._excluded_models:
				_logger.debug(f"{START_LOG_TEXT} is {L_RED}excluded{RESET}.")
				continue

			middle_log_text = "succesful registered with"
			if model in self._hidden_models:
				admin_class = admin_reg_settings.HIDDEN_ADMIN_CLASS
				middle_log_text = "was hidden by"
			elif model in self._admin_classes_for_models:
				admin_class = self._admin_classes_for_models[model]
			else:
				admin_class = self._admins_resolver(model)

			site.register(model, admin_class)
			_logger.debug(
				f"{START_LOG_TEXT} {middle_log_text} {L_GREEN}{typename(admin_class)}{RESET} admin class."
			)
