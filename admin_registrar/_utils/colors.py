from logging import getLogger
from admin_registrar.conf import settings, Settings



L_GREEN = ""
L_RED = ""
L_MAGENTA = ""
RESET = ""

__all__ = [
	'L_GREEN',
	'L_RED',
	'L_MAGENTA',
	'RESET'
]

_logger = getLogger(__name__)
if settings.COLORED_LOGS:
	try:
		from colorama import Fore as ColoramaFore, Style, init

		init()
		L_GREEN 	= ColoramaFore.LIGHTGREEN_EX
		L_RED 		= ColoramaFore.LIGHTRED_EX
		L_MAGENTA 	= ColoramaFore.LIGHTMAGENTA_EX
		RESET 		= Style.RESET_ALL
	except ImportError:
		_logger.error(f"The {Settings.COLORED_LOGS} parameter has been set, but you do not have the 'colorama' package installed.")
	# TODO: Add use raw ansi-es fallback settings option
