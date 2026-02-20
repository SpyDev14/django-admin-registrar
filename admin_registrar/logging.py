from admin_registrar.utils.colors import Fore


RECCOMENDED_FORMATTER = {
	'format': '[{levelname}] %sAdmin registrar%s: {message}' % (Fore.CYAN, Fore.RESET),
	'style': '{',
},

# TODO: Добавить форматтер или обработчик, вырезающий ANSI коды по этому регексу:
# re.compile('\001?\033\\[((?:\\d|;)*)([a-zA-Z])\002?')
