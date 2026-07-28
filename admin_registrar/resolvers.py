from typing import Protocol

from django.contrib.admin import ModelAdmin
from django.db.models import Model

from admin_registrar.conf import settings


class DefaultAdminsResolver(Protocol):
	def __call__(self, model_class: type[Model]) -> type[ModelAdmin]: ...

def first_mro_match_resolver(model_class: type[Model]) -> type[ModelAdmin]:
	for cls in model_class.mro():
		if not issubclass(cls, Model):
			continue # If model nesting from some mixins who not nested from Model
		if cls in settings.ADMINS_FOR_MODELS:
			return settings.ADMINS_FOR_MODELS[cls]
	return ModelAdmin
