# CI
# from admin_registrar.conf import settings

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

class _ForePalette(_Palette):
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

# TODO: Write normal comment
# I just wanted Fore marked green as class, not ligt-blue as var.
# It is one reason why i use classes dirrectly and metaclass for resolving.
# But i don't thing what metaclass and class as object is really bad in
# comparing with class and instance. Come one, class is regular object!
# And metaclass is regular class what just making other classes.

# Main reason why i use metaclass instead instance of regular class (what similar
# overwrite self to _Palette or _ForePalette) is avoid from `# type: ignore`. Yeap.

# Sometimes ago choosing class (empty or with ansi codes) was in `if` in
# global space (code in __getattribute__ was in global space), but it
# start leads to Circular Import
class _UnsolvedForeMeta(type):
	def __getattribute__(self, name):
		from admin_registrar.conf import settings
		global Fore

		Fore = _Palette
		if settings.ENABLE_COLORED_LOGS:
			try: from colorama import init; init()
			except ImportError:
				pass
			Fore = _ForePalette
		return getattr(Fore, name)

# Equals to _UnsolvedFore = _UnsolvedForeMeta("_UnsolvedFore", (_PlugPalette,), {})
class _UnsolvedFore(_Palette, metaclass=_UnsolvedForeMeta):
	pass


Fore: type[_Palette] = _UnsolvedFore
