from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from engine.math.vector2 import Vector2

if TYPE_CHECKING:
    from engine.ui.core.element import Element


@dataclass
class UIEvent:
    """Base UI event with bubbling support."""
    target: Element | None = None        # element that originally triggered
    current_target: Element | None = None # element currently handling
    _stopped: bool = False

    def stop_propagation(self) -> None:
        self._stopped = True

    @property
    def propagation_stopped(self) -> bool:
        return self._stopped


@dataclass
class ClickEvent(UIEvent):
    x: float = 0.0
    y: float = 0.0
    button: int = 1  # 1=left, 2=middle, 3=right


@dataclass
class HoverEvent(UIEvent):
    x: float = 0.0
    y: float = 0.0


@dataclass
class HoverExitEvent(UIEvent):
    pass


@dataclass
class FocusEvent(UIEvent):
    pass


@dataclass
class BlurEvent(UIEvent):
    pass


@dataclass
class ScrollEvent(UIEvent):
    delta: float = 0.0
