import sys

if sys.version_info >= (3, 13):
	from warnings import deprecated # novermin
else:
	from typing_extensions import deprecated
