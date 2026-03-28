from __future__ import annotations

import ctypes

from sdl2 import (
    SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP, SDL_MOUSEMOTION, SDL_MOUSEWHEEL,
    SDL_GetMouseState,
)

from engine.math.vector2 import Vector2
from engine.input.keys import MouseButton


class Mouse:
    def __init__(self) -> None:
        self._position = Vector2.zero()
        self._current: set[int] = set()
        self._previous: set[int] = set()
        self._scroll_delta: float = 0.0

    def process_event(self, event) -> None:
        if event.type == SDL_MOUSEMOTION:
            self._position = Vector2(event.motion.x, event.motion.y)
        elif event.type == SDL_MOUSEBUTTONDOWN:
            self._current.add(event.button.button)
        elif event.type == SDL_MOUSEBUTTONUP:
            self._current.discard(event.button.button)
        elif event.type == SDL_MOUSEWHEEL:
            self._scroll_delta += event.wheel.y

    def update(self) -> None:
        self._previous = self._current.copy()
        self._scroll_delta = 0.0

    @property
    def position(self) -> Vector2:
        return self._position

    @property
    def scroll_delta(self) -> float:
        return self._scroll_delta

    def is_pressed(self, button: MouseButton) -> bool:
        return int(button) in self._current

    def is_just_pressed(self, button: MouseButton) -> bool:
        b = int(button)
        return b in self._current and b not in self._previous

    def is_just_released(self, button: MouseButton) -> bool:
        b = int(button)
        return b not in self._current and b in self._previous
