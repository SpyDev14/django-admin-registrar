

from typing import AbstractSet, Iterable, Sequence, TypeAlias, TypeVar

_T = TypeVar('_T')
OneOrSequence: TypeAlias = _T | Sequence[_T]

def one_or_seq_to_seq(T: type[_T], one_or_seq: OneOrSequence[_T]) -> Sequence[_T]:
	if isinstance(one_or_seq, T):
		return (one_or_seq,)
	return one_or_seq # type: ignore[reportReturnType]

class IterableAbstractSet(AbstractSet[_T], Iterable[_T]):
	"""`isinstance` IS NOT SUPPORTED"""
	pass
