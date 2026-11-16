
from typing import Final, Literal, TypeAlias
from enum import Enum


class _Unset(Enum):
	UNSET = None

	def __bool__(self) -> Literal[False]:
		return False

	def __repr__(self) -> str:
		return "<UNSET>"


UNSET: Final = _Unset.UNSET
UnsetT: TypeAlias = Literal[_Unset.UNSET]
