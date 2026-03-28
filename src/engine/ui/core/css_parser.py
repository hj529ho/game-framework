"""CSS string parser.

Parses CSS property strings into a dict of resolved values.

Supports:
  - Length values: "100px", "50%", "auto"
  - Color values: "#ff0000", "#f00", "rgb(255, 0, 0)", "rgba(255, 0, 0, 0.5)"
  - Named colors: "red", "blue", "white", "transparent", etc.
  - Shorthand: padding, margin, border, border-radius, gap
  - Flex properties: display, flex-direction, justify-content, align-items, flex-grow, etc.
  - Position: position, top, right, bottom, left
  - Text: font-family, font-size, color, text-align
  - Opacity: opacity
"""
from __future__ import annotations

import re

from engine.renderer.color import Color


# Named CSS colors
_NAMED_COLORS: dict[str, Color] = {
    "white": Color(255, 255, 255),
    "black": Color(0, 0, 0),
    "red": Color(255, 0, 0),
    "green": Color(0, 128, 0),
    "lime": Color(0, 255, 0),
    "blue": Color(0, 0, 255),
    "yellow": Color(255, 255, 0),
    "cyan": Color(0, 255, 255),
    "magenta": Color(255, 0, 255),
    "orange": Color(255, 165, 0),
    "gray": Color(128, 128, 128),
    "grey": Color(128, 128, 128),
    "darkgray": Color(64, 64, 64),
    "darkgrey": Color(64, 64, 64),
    "lightgray": Color(192, 192, 192),
    "lightgrey": Color(192, 192, 192),
    "transparent": Color(0, 0, 0, 0),
    "purple": Color(128, 0, 128),
    "pink": Color(255, 192, 203),
    "brown": Color(139, 69, 19),
    "navy": Color(0, 0, 128),
    "teal": Color(0, 128, 128),
    "gold": Color(255, 215, 0),
    "silver": Color(192, 192, 192),
}


def parse_css(css_string: str) -> dict[str, str]:
    """Parse a CSS string into a dict of property -> raw value.

    Example:
        parse_css("width: 200px; padding: 10px 20px; background: #333")
        -> {"width": "200px", "padding": "10px 20px", "background": "#333"}
    """
    result = {}
    for declaration in css_string.split(";"):
        declaration = declaration.strip()
        if not declaration or ":" not in declaration:
            continue
        prop, _, value = declaration.partition(":")
        result[prop.strip()] = value.strip()
    return result


def parse_length(value: str) -> tuple[float, str]:
    """Parse a CSS length value. Returns (number, unit).

    "100px" -> (100, "px")
    "50%"   -> (50, "%")
    "auto"  -> (0, "auto")
    "0"     -> (0, "px")
    """
    value = value.strip()
    if value == "auto":
        return 0.0, "auto"
    if value == "none":
        return 0.0, "none"
    if value.endswith("px"):
        return float(value[:-2]), "px"
    if value.endswith("%"):
        return float(value[:-1]), "%"
    try:
        return float(value), "px"
    except ValueError:
        return 0.0, "auto"


def parse_color(value: str) -> Color | None:
    """Parse a CSS color value.

    Supports: #rgb, #rrggbb, #rrggbbaa, rgb(), rgba(), named colors.
    """
    value = value.strip().lower()

    # Named colors
    if value in _NAMED_COLORS:
        return _NAMED_COLORS[value]

    # Hex
    if value.startswith("#"):
        hex_str = value[1:]
        if len(hex_str) == 3:
            r = int(hex_str[0] * 2, 16)
            g = int(hex_str[1] * 2, 16)
            b = int(hex_str[2] * 2, 16)
            return Color(r, g, b)
        elif len(hex_str) == 6:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return Color(r, g, b)
        elif len(hex_str) == 8:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            a = int(hex_str[6:8], 16)
            return Color(r, g, b, a)

    # rgb(r, g, b) / rgba(r, g, b, a)
    m = re.match(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)', value)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if m.group(4) is not None:
            alpha_val = float(m.group(4))
            # CSS standard: alpha is 0.0~1.0
            a = int(alpha_val * 255) if alpha_val <= 1.0 else int(min(alpha_val, 255))
        else:
            a = 255
        return Color(r, g, b, a)

    return None


def parse_edge_shorthand(value: str) -> tuple[float, float, float, float]:
    """Parse CSS shorthand for margin/padding.

    "10px"              -> (10, 10, 10, 10)
    "10px 20px"         -> (10, 20, 10, 20)
    "10px 20px 30px"    -> (10, 20, 30, 20)
    "10px 20px 30px 40px" -> (10, 20, 30, 40)
    """
    parts = value.split()
    values = [parse_length(p)[0] for p in parts]

    if len(values) == 1:
        return values[0], values[0], values[0], values[0]
    elif len(values) == 2:
        return values[0], values[1], values[0], values[1]
    elif len(values) == 3:
        return values[0], values[1], values[2], values[1]
    elif len(values) >= 4:
        return values[0], values[1], values[2], values[3]
    return 0, 0, 0, 0
