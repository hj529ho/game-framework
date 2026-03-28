from __future__ import annotations

from typing import TYPE_CHECKING

from sdl2 import SDL_Rect, SDL_RenderCopy

from engine.ui.core.element import Element
from engine.ui.core.style import Style
from engine.ui.renderer import draw_box

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer


class Image(Element):
    """Image display element. Like HTML <img>.

    Examples:
        Image("icons/heart.png", style="width: 32px; height: 32px")
    """

    def __init__(self, src: str = "", style: Style | str | None = None, **kwargs) -> None:
        super().__init__(style=style, **kwargs)
        self._src = src
        self._texture = None
        self._img_w: int = 0
        self._img_h: int = 0

    @property
    def src(self) -> str:
        return self._src

    @src.setter
    def src(self, path: str) -> None:
        self._src = path
        self._texture = None

    def _ensure_loaded(self) -> None:
        if self._texture is None and self._src:
            from engine.core.app import current_app
            res = current_app().resources
            self._texture = res.load_image(self._src)
            self._img_w, self._img_h = res.get_image_size(self._src)

    def _draw_self(self, renderer: Renderer, ox: float, oy: float) -> None:
        s = self.style
        x = self._computed_x + ox
        y = self._computed_y + oy

        draw_box(
            renderer, x, y, self._computed_w, self._computed_h,
            background=s.background_color,
            border_color=s.border_color,
            border_width=s.border_width,
            border_radius=s.border_radius,
            opacity=s.opacity,
        )

        self._ensure_loaded()
        if self._texture is None:
            return

        ix = x + s.padding.left + s.border_width
        iy = y + s.padding.top + s.border_width
        iw = int(self._computed_w - s.padding.horizontal - s.border_width * 2)
        ih = int(self._computed_h - s.padding.vertical - s.border_width * 2)

        if iw <= 0 or ih <= 0:
            return

        dst = SDL_Rect(int(ix), int(iy), iw, ih)
        tex = self._texture

        def _draw():
            SDL_RenderCopy(renderer.sdl_renderer, tex, None, dst)
        renderer._enqueue(1001, _draw)
