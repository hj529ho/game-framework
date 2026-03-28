from __future__ import annotations

import math as _math

from engine.math.vector2 import Vector2
from engine.math.rect import Rect


class Circle:
    __slots__ = ('center', 'radius')

    def __init__(self, center: Vector2, radius: float) -> None:
        self.center = center
        self.radius = float(radius)

    def contains_point(self, point: Vector2) -> bool:
        return self.center.distance_to(point) <= self.radius

    def overlaps_circle(self, other: Circle) -> bool:
        dist = self.center.distance_to(other.center)
        return dist < self.radius + other.radius

    def overlaps_rect(self, rect: Rect) -> bool:
        closest_x = max(rect.left, min(self.center.x, rect.right))
        closest_y = max(rect.top, min(self.center.y, rect.bottom))
        dx = self.center.x - closest_x
        dy = self.center.y - closest_y
        return (dx * dx + dy * dy) < (self.radius * self.radius)

    def get_bounds(self) -> Rect:
        return Rect(
            self.center.x - self.radius,
            self.center.y - self.radius,
            self.radius * 2,
            self.radius * 2,
        )

    def __repr__(self) -> str:
        return f"Circle({self.center}, {self.radius})"
