from django.apps import AppConfig


class AdminRegistrarConfig(AppConfig):
	name = "admin_registrar"

	def ready(self) -> None:
		import admin_registrar.checks
