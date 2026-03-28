from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING

from sdl2 import (
    SDL_CreateTextureFromSurface, SDL_FreeSurface, SDL_DestroyTexture,
    SDL_QueryTexture,
)
from sdl2.sdlttf import TTF_RenderUTF8_Blended

from engine.ecs.component import Component
from engine.renderer.color import Color
from engine.math.vector2 import Vector2

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer


class TextRenderer(Component):
    """Component that renders text at the entity's position.

    Example:
        label = Entity("ScoreLabel")
        label.position = Vector2(10, 10)
        text = label.add_component(TextRenderer())
        text.text = "Score: 0"
        text.font = "fonts/arial.ttf"
        text.font_size = 24
        text.color = Color.WHITE
    """

    def __init__(
        self,
        text: str = "",
        font: str = "",
        font_size: int = 16,
        color: Color | None = None,
        layer: int = 0,
    ) -> None:
        super().__init__()
        self._text = text
        self._font_path = font
        self._font_size = font_size
        self._color = color or Color.WHITE
        self.layer = layer
        self.anchor = Vector2(0.0, 0.0)  # top-left by default

        self._texture = None
        self._width: int = 0
        self._height: int = 0
        self._dirty = True

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if value != self._text:
            self._text = value
            self._dirty = True

    @property
    def font(self) -> str:
        return self._font_path

    @font.setter
    def font(self, path: str) -> None:
        if path != self._font_path:
            self._font_path = path
            self._dirty = True

    @property
    def font_size(self) -> int:
        return self._font_size

    @font_size.setter
    def font_size(self, size: int) -> None:
        if size != self._font_size:
            self._font_size = size
            self._dirty = True

    @property
    def color(self) -> Color:
        return self._color

    @color.setter
    def color(self, c: Color) -> None:
        if c != self._color:
            self._color = c
            self._dirty = True

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def _rebuild(self) -> None:
        if not self._text or not self._font_path:
            self._texture = None
            self._width = 0
            self._height = 0
            return

        from engine.core.app import current_app
        app = current_app()

        # Free old texture
        if self._texture:
            SDL_DestroyTexture(self._texture)
            self._texture = None

        font = app.resources.load_font(self._font_path, self._font_size)

        from sdl2 import SDL_Color
        sdl_color = SDL_Color(self._color.r, self._color.g, self._color.b, self._color.a)
        surface = TTF_RenderUTF8_Blended(font, self._text.encode('utf-8'), sdl_color)
        if not surface:
            return

        self._texture = SDL_CreateTextureFromSurface(app.renderer.sdl_renderer, surface)
        SDL_FreeSurface(surface)

        if self._texture:
            w, h = ctypes.c_int(), ctypes.c_int()
            SDL_QueryTexture(self._texture, None, None, ctypes.byref(w), ctypes.byref(h))
            self._width = w.value
            self._height = h.value

        self._dirty = False

    def on_draw(self, renderer: Renderer) -> None:
        if self._dirty:
            self._rebuild()
        if self._texture is None:
            return

        pos = self.position
        x = pos.x - self._width * self.anchor.x
        y = pos.y - self._height * self.anchor.y

        renderer.draw_texture(
            self._texture,
            x, y,
            width=self._width,
            height=self._height,
            layer=self.layer,
        )

    def on_destroy(self) -> None:
        if self._texture:
            SDL_DestroyTexture(self._texture)
            self._texture = None
