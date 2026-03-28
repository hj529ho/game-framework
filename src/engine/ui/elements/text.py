from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING

from sdl2 import (
    SDL_CreateTextureFromSurface, SDL_FreeSurface, SDL_DestroyTexture,
    SDL_QueryTexture, SDL_Rect, SDL_Color, SDL_RenderCopy,
)
from sdl2.sdlttf import TTF_RenderUTF8_Blended

from engine.ui.core.element import Element
from engine.ui.core.style import Style
from engine.renderer.color import Color

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer


class Text(Element):
    """Text display element. Like HTML <span> or text node.

    Examples:
        Text("Score: 0", style="font: 'fonts/mono.ttf'; font-size: 18px; color: white")

        Text("HP: 100", style="color: red; font-size: 24px",
             class_name="hud-text")
    """

    def __init__(self, content: str = "", style: Style | str | None = None, **kwargs) -> None:
        super().__init__(style=style, **kwargs)
        self._content = content
        self._texture = None
        self._tex_w: int = 0
        self._tex_h: int = 0
        self._text_dirty = True

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        if value != self._content:
            self._content = value
            self._text_dirty = True
            self._mark_dirty()

    def _rebuild_texture(self, renderer: Renderer) -> None:
        if self._texture:
            SDL_DestroyTexture(self._texture)
            self._texture = None
            self._tex_w = 0
            self._tex_h = 0

        if not self._content:
            self._text_dirty = False
            return

        s = self.style
        font_path = s.font
        if not font_path:
            self._text_dirty = False
            return

        from engine.core.app import current_app
        font = current_app().resources.load_font(font_path, s.font_size)

        c = s.color or Color.WHITE
        sdl_color = SDL_Color(c.r, c.g, c.b, c.a)
        surface = TTF_RenderUTF8_Blended(font, self._content.encode('utf-8'), sdl_color)
        if not surface:
            self._text_dirty = False
            return

        self._texture = SDL_CreateTextureFromSurface(renderer.sdl_renderer, surface)
        SDL_FreeSurface(surface)

        if self._texture:
            w, h = ctypes.c_int(), ctypes.c_int()
            SDL_QueryTexture(self._texture, None, None, ctypes.byref(w), ctypes.byref(h))
            self._tex_w = w.value
            self._tex_h = h.value

            if self.style.width.is_auto():
                self._computed_w = self._tex_w + self.style.padding.horizontal
            if self.style.height.is_auto():
                self._computed_h = self._tex_h + self.style.padding.vertical

        self._text_dirty = False

    def _draw_self(self, renderer: Renderer, ox: float, oy: float) -> None:
        if self._text_dirty:
            self._rebuild_texture(renderer)
        if self._texture is None:
            return

        s = self.style
        x = self._computed_x + ox + s.padding.left
        y = self._computed_y + oy + s.padding.top

        available_w = self._computed_w - s.padding.horizontal
        if s.text_align == "center":
            x += (available_w - self._tex_w) / 2
        elif s.text_align == "right":
            x += available_w - self._tex_w

        dst = SDL_Rect(int(x), int(y), self._tex_w, self._tex_h)
        tex = self._texture

        def _draw():
            SDL_RenderCopy(renderer.sdl_renderer, tex, None, dst)
        renderer._enqueue(1001, _draw)

    def __del__(self) -> None:
        if self._texture:
            SDL_DestroyTexture(self._texture)
            self._texture = None
