from logging 	import getLogger
from typing 	import Callable

from django.contrib.admin 	import ModelAdmin, site, options
from django.db.models 		import Model
from django.apps 			import AppConfig

from admin_registrar.resolvers	import first_mro_match_resolver
from admin_registrar.utils 		import typename
from admin_registrar.conf 		import admin_reg_settings


_L_GREEN = ""
_L_RED = ""
_L_MAGENTA = ""
_RESET = ""

_logger = getLogger(__name__)

if admin_reg_settings.COLORED_LOGS:
	try:
		from colorama import Fore, Style, init
		init()
		_L_GREEN = f"{Style.BRIGHT}{Fore.GREEN}"
		_L_RED = f"{Style.BRIGHT}{Fore.RED}"
		_L_MAGENTA = f"{Style.BRIGHT}{Fore.MAGENTA}"
		_RESET = Style.RESET_ALL
	except ImportError:
		# _logger.error(f"The COLORED_LOGS parameter has been set, but you do not have the 'colorama' package installed.")
		COMM = '\033['
		_L_GREEN = COMM + "1;32m"
		_L_RED   = COMM + "1;31m"
		_RESET   = COMM + '0m'
		_L_MAGENTA = COMM + "1;35m"

class AdminRegistrator:
	def __init__(self,
			app: AppConfig,
			*,
			classes_for_models: dict[type[Model], type[ModelAdmin]] | None = None,
			excluded_models: 	set[type[Model]] | None = None,
			hidden_models: 		set[type[Model]] | None = None,

			default_class_resolver: Callable[[type[Model]], type[ModelAdmin]] = first_mro_match_resolver,
		):
		self._app = app
		self._excluded_models 	= excluded_models or set()
		self._hidden_models 	= hidden_models or set()
		self._admin_classes_for_models = classes_for_models or dict()
		self._default_admin_class_for_model_resolver = default_class_resolver

	def exclude(self, model: type[Model]):
		self._excluded_models.add(model)

	def exclude_inline(self, inline_class: type[options.InlineModelAdmin]):
		self.exclude(inline_class.model)

	def set_admin_class_for_model(self, model: type[Model], admin_class: type[ModelAdmin]):
		self._admin_classes_for_models[model] = admin_class

	def set_for_model(self, model: type[Model]):
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
				f"model {_L_GREEN}{typename(model)}{_RESET} "
				f"from {_L_MAGENTA}{self._app.name}{_RESET}"
			)

			if model in self._excluded_models:
				_logger.debug(f"{START_LOG_TEXT} is {_L_RED}excluded{_RESET}.")
				continue

			middle_log_text = "succesful registered with"
			if model in self._hidden_models:
				admin_class = admin_reg_settings.HIDDEN_ADMIN_CLASS
				middle_log_text = "was hidden by"
			elif model in self._admin_classes_for_models:
				admin_class = self._admin_classes_for_models[model]
			else:
				admin_class = self._default_admin_class_for_model_resolver(model)

			site.register(model, admin_class)
			_logger.debug(
				f"{START_LOG_TEXT} {middle_log_text} {_L_GREEN}{typename(admin_class)}{_RESET} admin class."
			)
