from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class UnitType(Enum):
    PX = auto()       # fixed pixels
    PERCENT = auto()  # percentage of parent
    AUTO = auto()     # computed by layout


@dataclass(frozen=True)
class Unit:
    """CSS-like unit value.

    Usage:
        px(100)    -> 100 pixels
        pct(50)    -> 50% of parent
        auto       -> auto-computed
    """
    value: float
    type: UnitType

    def resolve(self, parent_size: float) -> float:
        if self.type == UnitType.PX:
            return self.value
        elif self.type == UnitType.PERCENT:
            return parent_size * self.value / 100.0
        else:  # AUTO
            return 0.0

    def is_auto(self) -> bool:
        return self.type == UnitType.AUTO

    def __repr__(self) -> str:
        if self.type == UnitType.PX:
            return f"{self.value}px"
        elif self.type == UnitType.PERCENT:
            return f"{self.value}%"
        return "auto"


# Factory functions
def px(value: float) -> Unit:
    return Unit(value, UnitType.PX)

def pct(value: float) -> Unit:
    return Unit(value, UnitType.PERCENT)

auto = Unit(0, UnitType.AUTO)
