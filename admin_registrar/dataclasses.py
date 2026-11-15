from dataclasses import dataclass
from admin_registrar.utils.colors import Fore

@dataclass
class RegisteringLogColors:
	model: str = Fore.L_GREEN
	admin_class: str = Fore.L_GREEN
	app: str = Fore.L_MAGENTA
	excluded: str = Fore.RED
	already_registered: str = Fore.RED
