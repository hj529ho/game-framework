from __future__ import annotations

from typing import TYPE_CHECKING

from engine.ui.core.element import Element
from engine.ui.core.style import Style
from engine.ui.renderer import draw_box

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer


class Div(Element):
    """Container element. Like HTML <div>.

    Examples:
        # CSS string style
        Div(style="width: 300px; height: 200px; background: rgba(40,40,40,0.8); "
                  "border: 1px solid white; border-radius: 8px; "
                  "padding: 10px; display: flex; flex-direction: column; gap: 5px")

        # With children
        panel = Div(style="display: flex; gap: 10px")
        panel.append(Text("Hello"))
        panel.append(Text("World"))
    """

    def __init__(self, style: Style | str | None = None, **kwargs) -> None:
        super().__init__(style=style, **kwargs)

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
