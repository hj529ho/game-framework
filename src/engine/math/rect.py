from __future__ import annotations

from engine.math.vector2 import Vector2


class Rect:
    __slots__ = ('x', 'y', 'width', 'height')

    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center(self) -> Vector2:
        return Vector2(self.x + self.width / 2, self.y + self.height / 2)

    @property
    def top_left(self) -> Vector2:
        return Vector2(self.x, self.y)

    @property
    def size(self) -> Vector2:
        return Vector2(self.width, self.height)

    def contains_point(self, point: Vector2) -> bool:
        return (self.x <= point.x <= self.x + self.width
                and self.y <= point.y <= self.y + self.height)

    def overlaps(self, other: Rect) -> bool:
        return (self.left < other.right and self.right > other.left
                and self.top < other.bottom and self.bottom > other.top)

    def intersection(self, other: Rect) -> Rect | None:
        left = max(self.left, other.left)
        top = max(self.top, other.top)
        right = min(self.right, other.right)
        bottom = min(self.bottom, other.bottom)
        if left < right and top < bottom:
            return Rect(left, top, right - left, bottom - top)
        return None

    def expanded(self, amount: float) -> Rect:
        return Rect(
            self.x - amount, self.y - amount,
            self.width + amount * 2, self.height + amount * 2,
        )

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.width, self.height)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rect):
            return NotImplemented
        return (self.x == other.x and self.y == other.y
                and self.width == other.width and self.height == other.height)

    def __repr__(self) -> str:
        return f"Rect({self.x}, {self.y}, {self.width}, {self.height})"
