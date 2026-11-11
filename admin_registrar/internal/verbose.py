from typing import Iterable, Sequence


def verb_list(iterable: Iterable[str]) -> str:
	"""
	["one", "2", "three"] -> "one, 2 or three"

	Convert iterable to sequence.
	"""
	seq = iterable if isinstance(iterable, Sequence) else tuple(iterable)

	if (len(seq) < 2):
		return ''.join(seq) # "" or str(seq[0])

	# "first, second or three"
	return ', '.join(seq[:-1]) + f" or {str(seq[-1])}"
