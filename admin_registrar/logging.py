from admin_registrar.utils.colors import Fore


RECOMMENDED_FORMATTER = {
	'format': '[{levelname}] %sAdmin registrar%s: {message}' % (Fore.CYAN, Fore.RESET),
	'style': '{',
}
RECOMMENDED_NAME = 'admin_registrar.registrars'
