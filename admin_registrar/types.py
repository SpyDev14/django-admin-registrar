
from typing import Protocol, Iterable, Any

from django.contrib.admin 	import ModelAdmin
from django.db.models 		import Model


class AdminsResolver(Protocol):
	def __call__(model_class: type[Model]) -> type[ModelAdmin]: ...

class RegisterOnSite(Protocol):
	def __call__(
		model_class: type[Model],
		admin_class: type[ModelAdmin],
	) -> None: ...
