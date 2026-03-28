from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, TYPE_CHECKING

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

if TYPE_CHECKING:
    from engine.renderer.camera import Camera2D


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

    def _get_camera(self) -> Camera2D | None:
        from engine.renderer.camera import Camera2D
        return Camera2D.get_active()

    def _world_to_screen(self, x: float, y: float) -> tuple[float, float]:
        cam = self._get_camera()
        if cam is None:
            return x, y
        pos = cam.world_to_screen(Vector2(x, y))
        return pos.x, pos.y

    def _world_scale(self) -> float:
        cam = self._get_camera()
        return cam.zoom if cam else 1.0

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
        world_space: bool = True,
    ) -> None:
        if world_space:
            sx, sy = self._world_to_screen(x, y)
            zoom = self._world_scale()
            rect = SDL_Rect(int(sx), int(sy), int(width * zoom), int(height * zoom))
        else:
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
        world_space: bool = True,
    ) -> None:
        if world_space:
            sx1, sy1 = self._world_to_screen(start.x, start.y)
            sx2, sy2 = self._world_to_screen(end.x, end.y)
        else:
            sx1, sy1 = start.x, start.y
            sx2, sy2 = end.x, end.y

        x1, y1, x2, y2 = int(sx1), int(sy1), int(sx2), int(sy2)

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
        world_space: bool = True,
    ) -> None:
        # Query texture size if not provided
        if width is None or height is None:
            w, h = ctypes.c_int(), ctypes.c_int()
            from sdl2 import SDL_QueryTexture
            SDL_QueryTexture(texture, None, None, ctypes.byref(w), ctypes.byref(h))
            width = width or w.value
            height = height or h.value

        if world_space:
            sx, sy = self._world_to_screen(x, y)
            zoom = self._world_scale()
            dst = SDL_Rect(int(sx), int(sy), int(width * zoom), int(height * zoom))
        else:
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

    def draw_circle(
        self,
        center: Vector2,
        radius: float,
        color: Color,
        filled: bool = True,
        layer: int = 0,
        world_space: bool = True,
    ) -> None:
        if world_space:
            sx, sy = self._world_to_screen(center.x, center.y)
            r = int(radius * self._world_scale())
        else:
            sx, sy = center.x, center.y
            r = int(radius)

        cx, cy = int(sx), int(sy)

        if filled:
            def _draw():
                self._set_color(color)
                _render_filled_circle(self._renderer, cx, cy, r)
        else:
            def _draw():
                self._set_color(color)
                _render_circle_outline(self._renderer, cx, cy, r)
        self._enqueue(layer, _draw)

    def draw_polygon(
        self,
        points: list[Vector2],
        color: Color,
        layer: int = 0,
        world_space: bool = True,
    ) -> None:
        """Draw a closed polygon outline."""
        if len(points) < 2:
            return

        if world_space:
            screen_pts = [self._world_to_screen(p.x, p.y) for p in points]
        else:
            screen_pts = [(p.x, p.y) for p in points]

        int_pts = [(int(x), int(y)) for x, y in screen_pts]

        def _draw():
            self._set_color(color)
            for i in range(len(int_pts)):
                x1, y1 = int_pts[i]
                x2, y2 = int_pts[(i + 1) % len(int_pts)]
                SDL_RenderDrawLine(self._renderer, x1, y1, x2, y2)
        self._enqueue(layer, _draw)


# Midpoint circle algorithm (SDL2 has no built-in circle drawing)

def _render_circle_outline(renderer, cx: int, cy: int, r: int) -> None:
    x, y = r, 0
    d = 1 - r
    while x >= y:
        SDL_RenderDrawLine(renderer, cx + x, cy + y, cx + x, cy + y)
        SDL_RenderDrawLine(renderer, cx - x, cy + y, cx - x, cy + y)
        SDL_RenderDrawLine(renderer, cx + x, cy - y, cx + x, cy - y)
        SDL_RenderDrawLine(renderer, cx - x, cy - y, cx - x, cy - y)
        SDL_RenderDrawLine(renderer, cx + y, cy + x, cx + y, cy + x)
        SDL_RenderDrawLine(renderer, cx - y, cy + x, cx - y, cy + x)
        SDL_RenderDrawLine(renderer, cx + y, cy - x, cx + y, cy - x)
        SDL_RenderDrawLine(renderer, cx - y, cy - x, cx - y, cy - x)
        y += 1
        if d < 0:
            d += 2 * y + 1
        else:
            x -= 1
            d += 2 * (y - x) + 1


def _render_filled_circle(renderer, cx: int, cy: int, r: int) -> None:
    x, y = r, 0
    d = 1 - r
    while x >= y:
        SDL_RenderDrawLine(renderer, cx - x, cy + y, cx + x, cy + y)
        SDL_RenderDrawLine(renderer, cx - x, cy - y, cx + x, cy - y)
        SDL_RenderDrawLine(renderer, cx - y, cy + x, cx + y, cy + x)
        SDL_RenderDrawLine(renderer, cx - y, cy - x, cx + y, cy - x)
        y += 1
        if d < 0:
            d += 2 * y + 1
        else:
            x -= 1
            d += 2 * (y - x) + 1
