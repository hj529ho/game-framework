from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from engine.ui.core.units import Unit, UnitType, px, pct, auto
from engine.ui.core.css_parser import parse_css, parse_length, parse_color, parse_edge_shorthand

if TYPE_CHECKING:
    from engine.renderer.color import Color


@dataclass
class EdgeInsets:
    """top, right, bottom, left (CSS order)."""
    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0
    left: float = 0.0

    @staticmethod
    def all(value: float) -> EdgeInsets:
        return EdgeInsets(value, value, value, value)

    @staticmethod
    def symmetric(vertical: float = 0, horizontal: float = 0) -> EdgeInsets:
        return EdgeInsets(vertical, horizontal, vertical, horizontal)

    @property
    def horizontal(self) -> float:
        return self.left + self.right

    @property
    def vertical(self) -> float:
        return self.top + self.bottom


def _parse_unit(raw: str) -> Unit:
    val, unit = parse_length(raw)
    if unit == "auto":
        return auto
    elif unit == "%":
        return pct(val)
    else:
        return px(val)


class Style:
    """CSS-like style. Accepts a CSS string or keyword arguments.

    Can be created in three ways:

    1. CSS string:
        Style("width: 200px; padding: 10px; background: #333")

    2. Keyword arguments (programmatic):
        Style(width=px(200), padding=EdgeInsets.all(10))

    3. Both (CSS string + overrides):
        Style("display: flex; gap: 10px", direction="row")
    """

    def __init__(self, css: str = "", **kwargs) -> None:
        # Sizing
        self.width: Unit = auto
        self.height: Unit = auto
        self.min_width: float = 0.0
        self.min_height: float = 0.0
        self.max_width: float = float('inf')
        self.max_height: float = float('inf')

        # Box model
        self.padding: EdgeInsets = EdgeInsets()
        self.margin: EdgeInsets = EdgeInsets()

        # Border
        self.border_width: float = 0.0
        self.border_color: Color | None = None
        self.border_radius: float = 0.0

        # Background
        self.background_color: Color | None = None
        self.background: Color | None = None  # alias
        self.opacity: float = 1.0

        # Layout
        self.display: str = "flex"
        self.direction: str = "column"       # flex-direction
        self.justify_content: str = "start"
        self.align_items: str = "start"
        self.gap: float = 0.0
        self.wrap: bool = False

        # Positioning
        self.position: str = "static"
        self.top: float | None = None
        self.right_pos: float | None = None  # 'right' as position
        self.bottom: float | None = None
        self.left_pos: float | None = None   # 'left' as position

        # Text
        self.font: str | None = None
        self.font_size: int = 16
        self.color: Color | None = None
        self.text_align: str = "left"

        # Flex item
        self.flex_grow: float = 0.0
        self.flex_shrink: float = 1.0

        # Parse CSS string first
        if css:
            self._apply_css(css)

        # Then apply keyword overrides
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)

    def _apply_css(self, css: str) -> None:
        props = parse_css(css)
        for prop, value in props.items():
            self._set_property(prop, value)

    def _set_property(self, prop: str, value: str) -> None:
        prop = prop.strip()
        value = value.strip()

        # Sizing
        if prop == "width":
            self.width = _parse_unit(value)
        elif prop == "height":
            self.height = _parse_unit(value)
        elif prop == "min-width":
            self.min_width = parse_length(value)[0]
        elif prop == "min-height":
            self.min_height = parse_length(value)[0]
        elif prop == "max-width":
            v, u = parse_length(value)
            self.max_width = v if u != "none" else float('inf')
        elif prop == "max-height":
            v, u = parse_length(value)
            self.max_height = v if u != "none" else float('inf')

        # Padding (shorthand)
        elif prop == "padding":
            t, r, b, l = parse_edge_shorthand(value)
            self.padding = EdgeInsets(t, r, b, l)
        elif prop == "padding-top":
            self.padding.top = parse_length(value)[0]
        elif prop == "padding-right":
            self.padding.right = parse_length(value)[0]
        elif prop == "padding-bottom":
            self.padding.bottom = parse_length(value)[0]
        elif prop == "padding-left":
            self.padding.left = parse_length(value)[0]

        # Margin (shorthand)
        elif prop == "margin":
            t, r, b, l = parse_edge_shorthand(value)
            self.margin = EdgeInsets(t, r, b, l)
        elif prop == "margin-top":
            self.margin.top = parse_length(value)[0]
        elif prop == "margin-right":
            self.margin.right = parse_length(value)[0]
        elif prop == "margin-bottom":
            self.margin.bottom = parse_length(value)[0]
        elif prop == "margin-left":
            self.margin.left = parse_length(value)[0]

        # Border
        elif prop == "border-width":
            self.border_width = parse_length(value)[0]
        elif prop == "border-color":
            self.border_color = parse_color(value)
        elif prop == "border-radius":
            self.border_radius = parse_length(value)[0]
        elif prop == "border":
            # shorthand: "1px solid #fff"
            parts = value.split()
            for p in parts:
                c = parse_color(p)
                if c:
                    self.border_color = c
                elif p not in ("solid", "dashed", "dotted", "none"):
                    v, u = parse_length(p)
                    if u == "px":
                        self.border_width = v

        # Background
        elif prop in ("background", "background-color"):
            c = parse_color(value)
            if c:
                self.background_color = c
                self.background = c

        # Opacity
        elif prop == "opacity":
            try:
                self.opacity = float(value)
            except ValueError:
                pass

        # Display & Flex
        elif prop == "display":
            self.display = value
        elif prop == "flex-direction":
            self.direction = value
        elif prop == "justify-content":
            self.justify_content = value.replace("flex-", "")  # flex-start -> start
        elif prop == "align-items":
            self.align_items = value.replace("flex-", "")
        elif prop == "gap":
            self.gap = parse_length(value)[0]
        elif prop == "flex-wrap":
            self.wrap = (value == "wrap")
        elif prop == "flex-grow":
            try:
                self.flex_grow = float(value)
            except ValueError:
                pass
        elif prop == "flex-shrink":
            try:
                self.flex_shrink = float(value)
            except ValueError:
                pass

        # Position
        elif prop == "position":
            self.position = value
        elif prop == "top":
            self.top = parse_length(value)[0]
        elif prop == "right":
            self.right_pos = parse_length(value)[0]
        elif prop == "bottom":
            self.bottom = parse_length(value)[0]
        elif prop == "left":
            self.left_pos = parse_length(value)[0]

        # Text
        elif prop in ("font-family", "font"):
            # Remove quotes
            self.font = value.strip("'\"")
        elif prop == "font-size":
            self.font_size = int(parse_length(value)[0])
        elif prop == "color":
            self.color = parse_color(value)
        elif prop == "text-align":
            self.text_align = value

    def copy(self) -> Style:
        import copy
        return copy.copy(self)

    # For style inheritance
    _INHERITED_PROPERTIES = ("color", "font", "font_size", "text_align")

    def resolve_inherited(self, parent: Style | None) -> None:
        """Inherit properties from parent style (CSS inheritance)."""
        if parent is None:
            return
        for prop in Style._INHERITED_PROPERTIES:
            if getattr(self, prop) is None and getattr(parent, prop) is not None:
                setattr(self, prop, getattr(parent, prop))
