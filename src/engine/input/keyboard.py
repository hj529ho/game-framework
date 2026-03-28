from __future__ import annotations

from sdl2 import SDL_KEYDOWN, SDL_KEYUP

from engine.input.keys import Key


class Keyboard:
    def __init__(self) -> None:
        self._current: set[int] = set()
        self._previous: set[int] = set()

    def process_event(self, event) -> None:
        if event.type == SDL_KEYDOWN:
            self._current.add(event.key.keysym.sym)
        elif event.type == SDL_KEYUP:
            self._current.discard(event.key.keysym.sym)

    def update(self) -> None:
        self._previous = self._current.copy()

    def is_pressed(self, key: Key) -> bool:
        return int(key) in self._current

    def is_just_pressed(self, key: Key) -> bool:
        k = int(key)
        return k in self._current and k not in self._previous

    def is_just_released(self, key: Key) -> bool:
        k = int(key)
        return k not in self._current and k in self._previous
