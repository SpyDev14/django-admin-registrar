from logging import getLogger
from typing import Protocol

from admin_registrar.conf import settings, Settings

_logger = getLogger(__name__)

class _Palette:
	BLACK: 	str = ''
	RED: 	str = ''
	GREEN: 	str = ''
	YELLOW: str = ''
	BLUE: 	str = ''
	MAGENTA: str= ''
	CYAN: 	str = ''
	WHITE: 	str = ''

	L_BLACK: 	str = ''
	L_RED: 		str = ''
	L_GREEN: 	str = ''
	L_YELLOW: 	str = ''
	L_BLUE: 	str = ''
	L_MAGENTA: 	str = ''
	L_CYAN: 	str = ''
	L_WHITE: 	str = ''

	RESET: str = ''

class _AnsiPalette(_Palette):
	BLACK: 	str = '\033[30m'
	RED: 	str = '\033[31m'
	GREEN: 	str = '\033[32m'
	YELLOW: str = '\033[33m'
	BLUE: 	str = '\033[34m'
	MAGENTA: str= '\033[35m'
	CYAN: 	str = '\033[36m'
	WHITE: 	str = '\033[37m'

	L_BLACK: 	str = '\033[90m'
	L_RED: 		str = '\033[91m'
	L_GREEN: 	str = '\033[92m'
	L_YELLOW: 	str = '\033[93m'
	L_BLUE: 	str = '\033[94m'
	L_MAGENTA: 	str = '\033[95m'
	L_CYAN: 	str = '\033[96m'
	L_WHITE: 	str = '\033[97m'

	RESET: 	str = '\033[39m'

Fore: type[_Palette] = _Palette

if settings.COLORED_LOGS:
	try:
		from colorama import init
		init()
	except ImportError:
		pass
	# NOTE: Указать в документации, что поддерживается colorama init для cmd.exe

	Fore = _AnsiPalette
