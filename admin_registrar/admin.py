from django.contrib.admin import ModelAdmin

class HiddenAdmin(ModelAdmin):
	def get_model_perms(self, request):
		return {}
