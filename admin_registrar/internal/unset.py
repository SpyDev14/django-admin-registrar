
from typing import Final, Literal, TypeAlias
from enum import Enum

# class _UnsetType:
# 	_instance: Self | None = None

# 	def __new__(cls) -> Self:
# 		if cls._instance is None:
# 			cls._instance = super().__new__(cls)
# 		return cls._instance

# 	def __repr__(self) -> str:
# 		return "<UNSET>"

# 	def __bool__(self):
# 		return False

class _Unset(Enum):
	UNSET = None

UNSET: Final = _Unset.UNSET
UnsetT: TypeAlias = Literal[_Unset.UNSET]
