"""UI-specific rendering utilities for box model."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sdl2 import (
    SDL_SetRenderDrawColor, SDL_RenderFillRect, SDL_RenderDrawRect,
    SDL_SetRenderDrawBlendMode, SDL_BLENDMODE_BLEND, SDL_Rect,
)

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer
    from engine.renderer.color import Color


def draw_box(
    renderer: Renderer,
    x: float, y: float, w: float, h: float,
    background: Color | None = None,
    border_color: Color | None = None,
    border_width: float = 0,
    border_radius: float = 0,
    opacity: float = 1.0,
    layer: int = 1000,
) -> None:
    """Draw a UI box with optional background, border, and rounded corners."""
    sdl_r = renderer.sdl_renderer
    ix, iy, iw, ih = int(x), int(y), int(w), int(h)

    if iw <= 0 or ih <= 0:
        return

    def _draw():
        SDL_SetRenderDrawBlendMode(sdl_r, SDL_BLENDMODE_BLEND)

        # Background
        if background is not None:
            a = int(background.a * opacity)
            SDL_SetRenderDrawColor(sdl_r, background.r, background.g, background.b, a)

            if border_radius > 0:
                _fill_rounded_rect(sdl_r, ix, iy, iw, ih, int(border_radius))
            else:
                rect = SDL_Rect(ix, iy, iw, ih)
                SDL_RenderFillRect(sdl_r, rect)

        # Border
        if border_color is not None and border_width > 0:
            a = int(border_color.a * opacity)
            SDL_SetRenderDrawColor(sdl_r, border_color.r, border_color.g, border_color.b, a)

            bw = int(border_width)
            for i in range(bw):
                rect = SDL_Rect(ix + i, iy + i, iw - 2 * i, ih - 2 * i)
                SDL_RenderDrawRect(sdl_r, rect)

    renderer._enqueue(layer, _draw)


def _fill_rounded_rect(renderer, x: int, y: int, w: int, h: int, r: int) -> None:
    """Fill a rounded rectangle using horizontal lines."""
    from sdl2 import SDL_RenderDrawLine

    r = min(r, w // 2, h // 2)

    # Middle section (full width)
    for row in range(r, h - r):
        SDL_RenderDrawLine(renderer, x, y + row, x + w - 1, y + row)

    # Top and bottom rounded corners
    cx1, cy1 = x + r, y + r           # top-left center
    cx2, cy2 = x + w - r - 1, y + r   # top-right center
    cx3, cy3 = x + r, y + h - r - 1   # bottom-left center
    cx4, cy4 = x + w - r - 1, y + h - r - 1  # bottom-right center

    # Midpoint circle fill for corners
    px, py = r, 0
    d = 1 - r
    while px >= py:
        # Top section
        SDL_RenderDrawLine(renderer, cx1 - px, cy1 - py, cx2 + px, cy2 - py)
        SDL_RenderDrawLine(renderer, cx1 - py, cy1 - px, cx2 + py, cy2 - px)
        # Bottom section
        SDL_RenderDrawLine(renderer, cx3 - px, cy3 + py, cx4 + px, cy4 + py)
        SDL_RenderDrawLine(renderer, cx3 - py, cy3 + px, cx4 + py, cy4 + px)

        py += 1
        if d < 0:
            d += 2 * py + 1
        else:
            px -= 1
            d += 2 * (py - px) + 1
