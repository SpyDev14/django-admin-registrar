

from typing import Iterator, Protocol, Sequence, TypeAlias, TypeVar, runtime_checkable

_T = TypeVar('_T')
_T_co = TypeVar('_T_co', covariant=True)
OneOrSequence: TypeAlias = _T | Sequence[_T]

def one_or_seq_to_seq(T: type[_T], one_or_seq: OneOrSequence[_T]) -> Sequence[_T]:
	if isinstance(one_or_seq, T):
		return (one_or_seq,)
	return one_or_seq # type: ignore[reportReturnType]

@runtime_checkable
class ReadOnlySet(Protocol[_T_co]):
	def __contains__(self, item: object, /) -> bool: ...
	def __iter__(self) -> Iterator[_T_co]: ...
	def __len__(self) -> int: ...
