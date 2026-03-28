from __future__ import annotations

import math as _math


class Vector2:
    __slots__ = ('x', 'y')

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self.x = float(x)
        self.y = float(y)

    # Arithmetic
    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2:
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vector2:
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> Vector2:
        return Vector2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> Vector2:
        return Vector2(-self.x, -self.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2):
            return NotImplemented
        return _math.isclose(self.x, other.x) and _math.isclose(self.y, other.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    # Properties
    @property
    def magnitude(self) -> float:
        return _math.sqrt(self.x * self.x + self.y * self.y)

    @property
    def sqr_magnitude(self) -> float:
        return self.x * self.x + self.y * self.y

    @property
    def normalized(self) -> Vector2:
        mag = self.magnitude
        if mag == 0:
            return Vector2.zero()
        return Vector2(self.x / mag, self.y / mag)

    # Methods
    def dot(self, other: Vector2) -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: Vector2) -> float:
        return self.x * other.y - self.y * other.x

    def distance_to(self, other: Vector2) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return _math.sqrt(dx * dx + dy * dy)

    def angle_to(self, other: Vector2) -> float:
        return _math.degrees(_math.atan2(other.y - self.y, other.x - self.x))

    def lerp(self, other: Vector2, t: float) -> Vector2:
        return Vector2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
        )

    def rotate(self, angle_degrees: float) -> Vector2:
        rad = _math.radians(angle_degrees)
        cos_a = _math.cos(rad)
        sin_a = _math.sin(rad)
        return Vector2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a,
        )

    def copy(self) -> Vector2:
        return Vector2(self.x, self.y)

    # Named constructors
    @staticmethod
    def zero() -> Vector2:
        return Vector2(0.0, 0.0)

    @staticmethod
    def one() -> Vector2:
        return Vector2(1.0, 1.0)

    @staticmethod
    def up() -> Vector2:
        return Vector2(0.0, -1.0)

    @staticmethod
    def down() -> Vector2:
        return Vector2(0.0, 1.0)

    @staticmethod
    def left() -> Vector2:
        return Vector2(-1.0, 0.0)

    @staticmethod
    def right() -> Vector2:
        return Vector2(1.0, 0.0)

    @staticmethod
    def from_angle(degrees: float) -> Vector2:
        rad = _math.radians(degrees)
        return Vector2(_math.cos(rad), _math.sin(rad))

    # Tuple interop
    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        raise IndexError(f"Vector2 index {index} out of range")

    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"
