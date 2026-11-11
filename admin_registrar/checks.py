from typing import Sequence

from django.core.checks import ERROR, register, Tags, CheckMessage, WARNING

from admin_registrar.internal.reflection import typename
from admin_registrar import conf


class Codes:
	UNKNOWN_CONFIG_KEYS_WARNING = "W001"
	SPECIFIED_CVAR_VALUE_INVALID = "E001"

for name, value in ((attr, getattr(Codes, attr)) for attr in dir(Codes)):
	if not isinstance(value, str): continue
	if name.startswith('_'): continue
	if not name.isupper(): continue

	setattr(Codes, name, f"admin_registrar.{value}")


@register(Tags.admin)
def check_unknown_config_keys(*args, **kwargs) -> Sequence[CheckMessage]:
	config_dict = conf._get_config_dict()
	messages = []

	known_keys = conf.Config._get_known_keys_for_conf_dict()
	last: CheckMessage | None = None
	for unknown_key in config_dict.keys() - known_keys:
		messages.append(last := CheckMessage(
			WARNING, f"Unknown admin_registrar config key: \"{unknown_key}\"",
			id=Codes.UNKNOWN_CONFIG_KEYS_WARNING
		))

	if last is not None:
		last.hint = f"Maybe it's deprecated or typo? Known keys: {', '.join(known_keys)}."

	return messages

@register(Tags.admin)
def check_all_specified_cvars_valid(*args, **kwargs) -> Sequence[CheckMessage]:
	messages = []
	for cvar_attr in conf.Config._get_known_keys_for_conf_dict():
		try: getattr(conf.config, cvar_attr)
		except (conf.CVarTypeError, conf.CVarValueError) as ex:
			messages.append(CheckMessage(
				ERROR, f"{typename(ex)}: {ex}",
				id=Codes.SPECIFIED_CVAR_VALUE_INVALID
			))
	return messages
