from __future__ import annotations

from typing import TYPE_CHECKING

from engine.ui.core.element import Element
from engine.ui.core.style import Style
from engine.ui.renderer import draw_box
from engine.renderer.color import Color
from engine.math.utils import clamp

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer


class ProgressBar(Element):
    """A progress/health bar element.

    Examples:
        ProgressBar(0.75, style="width: 200px; height: 20px; "
                    "background: #333; border-radius: 4px")

        bar = ProgressBar(style="width: 100%; height: 16px; background: darkgray")
        bar.fill_color = Color.GREEN
        bar.value = 0.5
    """

    def __init__(self, value: float = 1.0, style: Style | str | None = None, **kwargs) -> None:
        super().__init__(style=style, **kwargs)
        self._value = clamp(value, 0.0, 1.0)
        self.fill_color: Color = Color.GREEN
        self.low_color: Color = Color.RED
        self.mid_color: Color = Color.YELLOW
        self.low_threshold: float = 0.25
        self.mid_threshold: float = 0.5
        self.auto_color: bool = True

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float) -> None:
        self._value = clamp(v, 0.0, 1.0)

    def _get_fill_color(self) -> Color:
        if not self.auto_color:
            return self.fill_color
        if self._value < self.low_threshold:
            return self.low_color
        if self._value < self.mid_threshold:
            return self.mid_color
        return self.fill_color

    def _draw_self(self, renderer: Renderer, ox: float, oy: float) -> None:
        s = self.style
        x = self._computed_x + ox
        y = self._computed_y + oy
        w = self._computed_w
        h = self._computed_h

        draw_box(
            renderer, x, y, w, h,
            background=s.background_color,
            border_color=s.border_color,
            border_width=s.border_width,
            border_radius=s.border_radius,
            opacity=s.opacity,
        )

        bw = s.border_width
        inner_x = x + bw
        inner_y = y + bw
        inner_w = (w - bw * 2) * self._value
        inner_h = h - bw * 2

        if inner_w > 0:
            draw_box(
                renderer, inner_x, inner_y, inner_w, inner_h,
                background=self._get_fill_color(),
                border_radius=max(0, s.border_radius - bw),
                opacity=s.opacity,
                layer=1001,
            )
