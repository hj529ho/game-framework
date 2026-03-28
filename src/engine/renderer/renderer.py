from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import ctypes

from sdl2 import (
    SDL_Renderer, SDL_SetRenderDrawColor, SDL_RenderClear, SDL_RenderPresent,
    SDL_RenderFillRect, SDL_RenderDrawRect, SDL_RenderDrawLine,
    SDL_RenderCopy, SDL_RenderCopyEx,
    SDL_Rect, SDL_SetRenderDrawBlendMode, SDL_BLENDMODE_BLEND,
    SDL_Texture,
)

from engine.math.vector2 import Vector2
from engine.renderer.color import Color


@dataclass(order=True)
class _DrawCommand:
    layer: int
    order: int = field(compare=True)
    draw_fn: Callable = field(compare=False)


class Renderer:
    def __init__(self, sdl_renderer: SDL_Renderer) -> None:
        self._renderer = sdl_renderer
        self._draw_queue: list[_DrawCommand] = []
        self._order_counter: int = 0
        self._clear_color = Color.BLACK

        SDL_SetRenderDrawBlendMode(self._renderer, SDL_BLENDMODE_BLEND)

    @property
    def sdl_renderer(self):
        return self._renderer

    @property
    def clear_color(self) -> Color:
        return self._clear_color

    @clear_color.setter
    def clear_color(self, color: Color) -> None:
        self._clear_color = color

    def begin_frame(self) -> None:
        self._draw_queue.clear()
        self._order_counter = 0
        c = self._clear_color
        SDL_SetRenderDrawColor(self._renderer, c.r, c.g, c.b, c.a)
        SDL_RenderClear(self._renderer)

    def end_frame(self) -> None:
        self._draw_queue.sort()
        for cmd in self._draw_queue:
            cmd.draw_fn()
        SDL_RenderPresent(self._renderer)

    def _enqueue(self, layer: int, draw_fn: Callable) -> None:
        self._draw_queue.append(_DrawCommand(layer, self._order_counter, draw_fn))
        self._order_counter += 1

    def _set_color(self, color: Color) -> None:
        SDL_SetRenderDrawColor(self._renderer, color.r, color.g, color.b, color.a)

    def draw_rect(
        self,
        x: float, y: float, width: float, height: float,
        color: Color,
        filled: bool = True,
        layer: int = 0,
    ) -> None:
        rect = SDL_Rect(int(x), int(y), int(width), int(height))
        if filled:
            def _draw():
                self._set_color(color)
                SDL_RenderFillRect(self._renderer, rect)
        else:
            def _draw():
                self._set_color(color)
                SDL_RenderDrawRect(self._renderer, rect)
        self._enqueue(layer, _draw)

    def draw_line(
        self,
        start: Vector2,
        end: Vector2,
        color: Color,
        layer: int = 0,
    ) -> None:
        x1, y1 = int(start.x), int(start.y)
        x2, y2 = int(end.x), int(end.y)

        def _draw():
            self._set_color(color)
            SDL_RenderDrawLine(self._renderer, x1, y1, x2, y2)
        self._enqueue(layer, _draw)

    def draw_texture(
        self,
        texture: SDL_Texture,
        x: float, y: float,
        width: int | None = None,
        height: int | None = None,
        angle: float = 0.0,
        layer: int = 0,
    ) -> None:
        # Query texture size if not provided
        if width is None or height is None:
            w, h = ctypes.c_int(), ctypes.c_int()
            from sdl2 import SDL_QueryTexture
            SDL_QueryTexture(texture, None, None, ctypes.byref(w), ctypes.byref(h))
            width = width or w.value
            height = height or h.value

        dst = SDL_Rect(int(x), int(y), width, height)

        if angle == 0.0:
            def _draw():
                SDL_RenderCopy(self._renderer, texture, None, dst)
        else:
            def _draw():
                SDL_RenderCopyEx(
                    self._renderer, texture, None, dst,
                    angle, None, 0,
                )
        self._enqueue(layer, _draw)
