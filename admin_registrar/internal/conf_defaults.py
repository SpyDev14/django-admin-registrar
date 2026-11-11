from typing import Any

from admin_registrar.resolvers import first_mro_match_resolver
from admin_registrar.types import DefaultAdminsResolver

DEFAULT_RESOLVER: DefaultAdminsResolver = first_mro_match_resolver
def get_default_admins_for_models() -> Any:
	return {}
