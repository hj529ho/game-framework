from __future__ import annotations

from abc import ABC, abstractmethod

from sdl2 import (
    SDL_SetRenderDrawColor, SDL_RenderFillRect, SDL_SetRenderDrawBlendMode,
    SDL_BLENDMODE_BLEND,
)

from engine.renderer.color import Color


class Transition(ABC):
    """Base class for scene transitions.

    A transition runs between two scenes. The SceneManager calls
    update() and draw() each frame while the transition is active.
    """

    def __init__(self, duration: float = 0.5) -> None:
        self._duration = duration
        self._elapsed: float = 0.0

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def progress(self) -> float:
        """0.0 to 1.0"""
        if self._duration <= 0:
            return 1.0
        return min(1.0, self._elapsed / self._duration)

    @property
    def is_complete(self) -> bool:
        return self._elapsed >= self._duration

    def update(self, dt: float) -> None:
        self._elapsed += dt

    @abstractmethod
    def draw(self, renderer) -> None:
        """Draw the transition effect. Called after scene draw."""
        pass


class FadeTransition(Transition):
    """Fade to a color (default black) and back.

    First half: fade out (0 -> full opacity)
    Second half: fade in (full opacity -> 0)

    The SceneManager should switch the scene at the midpoint.
    """

    def __init__(self, duration: float = 0.5, color: Color | None = None) -> None:
        super().__init__(duration)
        self._color = color or Color.BLACK

    @property
    def at_midpoint(self) -> bool:
        return self.progress >= 0.5

    def draw(self, renderer) -> None:
        # Alpha: 0 -> 255 -> 0
        p = self.progress
        if p <= 0.5:
            alpha = int(p * 2 * 255)
        else:
            alpha = int((1.0 - (p - 0.5) * 2) * 255)
        alpha = max(0, min(255, alpha))

        sdl_r = renderer.sdl_renderer
        c = self._color

        def _draw():
            SDL_SetRenderDrawBlendMode(sdl_r, SDL_BLENDMODE_BLEND)
            SDL_SetRenderDrawColor(sdl_r, c.r, c.g, c.b, alpha)
            SDL_RenderFillRect(sdl_r, None)

        renderer._enqueue(9999, _draw)


class SlideTransition(Transition):
    """Slide the old scene out and new scene in.

    Direction: "left", "right", "up", "down"
    """

    def __init__(self, duration: float = 0.5, direction: str = "left") -> None:
        super().__init__(duration)
        self.direction = direction
        self._offset_x: float = 0.0
        self._offset_y: float = 0.0

    @property
    def at_midpoint(self) -> bool:
        return self.progress >= 0.5

    def update(self, dt: float) -> None:
        super().update(dt)
        from engine.core.app import current_app
        app = current_app()
        w, h = app.width, app.height
        p = self.progress

        if self.direction == "left":
            self._offset_x = -p * w
        elif self.direction == "right":
            self._offset_x = p * w
        elif self.direction == "up":
            self._offset_y = -p * h
        elif self.direction == "down":
            self._offset_y = p * h

    @property
    def offset_x(self) -> float:
        return self._offset_x

    @property
    def offset_y(self) -> float:
        return self._offset_y

    def draw(self, renderer) -> None:
        # SlideTransition primarily provides offset values.
        # The scene manager/renderer should apply the offset.
        # As a fallback, we draw a wipe overlay.
        pass
