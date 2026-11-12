from typing import Any

from admin_registrar.types import DefaultAdminsResolver
from admin_registrar import resolvers

### ALLOWED INTERNAL IMPORT ###
DEFAULT_RESOLVER: DefaultAdminsResolver = resolvers.first_mro_match_resolver
def get_default_admins_for_models() -> Any: return {}
