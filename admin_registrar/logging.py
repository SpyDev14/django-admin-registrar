from admin_registrar.utils.colors import Fore


RECOMMENDED_FORMATTER = {
	'format': '[{levelname}] %sAdmin registrar%s: {message}' % (Fore.CYAN, Fore.RESET),
	'style': '{',
}
RECOMMENDED_NAME = 'admin_registrar.registrars'

# What about adding regex for match ANSI codes for removing or something like that?
# re.compile('\001?\033\\[((?:\\d|;)*)([a-zA-Z])\002?')
