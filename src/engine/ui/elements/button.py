from __future__ import annotations

from typing import TYPE_CHECKING

from engine.ui.core.element import Element
from engine.ui.core.style import Style
from engine.ui.elements.text import Text
from engine.ui.renderer import draw_box
from engine.renderer.color import Color

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer


class Button(Element):
    """Clickable button with text label. Has hover/active visual states.

    Examples:
        Button("Start Game", style="width: 200px; height: 50px; "
               "background: #3c3c3c; border-radius: 6px; "
               "font: 'fonts/ui.ttf'; font-size: 18px; color: white")

        btn = Button("OK")
        btn.on("click", lambda e: print("Clicked!"))
    """

    def __init__(self, label: str = "", style: Style | str | None = None, **kwargs) -> None:
        super().__init__(style=style, **kwargs)
        self._label = label
        self._label_element = Text(label)
        self._children.append(self._label_element)
        self._label_element._parent = self
        self._pressed = False

        self.hover_color: Color | None = None
        self.active_color: Color | None = None

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._label = value
        self._label_element.content = value

    def _get_bg_color(self) -> Color | None:
        base = self.style.background_color
        if self._pressed and self.active_color:
            return self.active_color
        if self._pressed and base:
            return Color(max(0, base.r - 30), max(0, base.g - 30), max(0, base.b - 30), base.a)
        if self._hovered and self.hover_color:
            return self.hover_color
        if self._hovered and base:
            return Color(min(255, base.r + 20), min(255, base.g + 20), min(255, base.b + 20), base.a)
        return base

    def _draw_self(self, renderer: Renderer, ox: float, oy: float) -> None:
        s = self.style
        x = self._computed_x + ox
        y = self._computed_y + oy

        draw_box(
            renderer, x, y, self._computed_w, self._computed_h,
            background=self._get_bg_color(),
            border_color=s.border_color,
            border_width=s.border_width,
            border_radius=s.border_radius,
            opacity=s.opacity,
        )

    def _draw_children(self, renderer: Renderer, ox: float, oy: float) -> None:
        s = self.style
        ls = self._label_element.style
        if s.font:
            ls.font = s.font
        if s.font_size:
            ls.font_size = s.font_size
        if s.color:
            ls.color = s.color
        ls.text_align = "center"

        self._label_element._computed_x = 0
        self._label_element._computed_y = 0
        self._label_element._computed_w = self._computed_w - s.padding.horizontal - s.border_width * 2
        self._label_element._computed_h = self._computed_h - s.padding.vertical - s.border_width * 2

        px_off = self._computed_x + ox + s.padding.left + s.border_width
        py_off = self._computed_y + oy + s.padding.top + s.border_width

        if self._label_element._tex_h > 0:
            available_h = self._computed_h - s.padding.vertical - s.border_width * 2
            self._label_element._computed_y = (available_h - self._label_element._tex_h) / 2

        self._label_element.draw(renderer, px_off, py_off)
