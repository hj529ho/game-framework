from __future__ import annotations


class Color:
    __slots__ = ('r', 'g', 'b', 'a')

    def __init__(self, r: int, g: int, b: int, a: int = 255) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def to_tuple(self) -> tuple[int, int, int, int]:
        return (self.r, self.g, self.b, self.a)

    def lerp(self, other: Color, t: float) -> Color:
        return Color(
            int(self.r + (other.r - self.r) * t),
            int(self.g + (other.g - self.g) * t),
            int(self.b + (other.b - self.b) * t),
            int(self.a + (other.a - self.a) * t),
        )

    def with_alpha(self, a: int) -> Color:
        return Color(self.r, self.g, self.b, a)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return NotImplemented
        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a

    def __hash__(self) -> int:
        return hash((self.r, self.g, self.b, self.a))

    def __repr__(self) -> str:
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"


# Named constants (defined after class body to avoid forward reference issues)
Color.WHITE = Color(255, 255, 255)
Color.BLACK = Color(0, 0, 0)
Color.RED = Color(255, 0, 0)
Color.GREEN = Color(0, 255, 0)
Color.BLUE = Color(0, 0, 255)
Color.YELLOW = Color(255, 255, 0)
Color.CYAN = Color(0, 255, 255)
Color.MAGENTA = Color(255, 0, 255)
Color.ORANGE = Color(255, 165, 0)
Color.GRAY = Color(128, 128, 128)
Color.DARK_GRAY = Color(64, 64, 64)
Color.LIGHT_GRAY = Color(192, 192, 192)
Color.TRANSPARENT = Color(0, 0, 0, 0)
