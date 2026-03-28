from __future__ import annotations

from engine.math.vector2 import Vector2


class Transform2D:
    __slots__ = ('position', 'rotation', 'scale')

    def __init__(
        self,
        position: Vector2 | None = None,
        rotation: float = 0.0,
        scale: Vector2 | None = None,
    ) -> None:
        self.position = position or Vector2.zero()
        self.rotation = rotation
        self.scale = scale or Vector2.one()

    @property
    def forward(self) -> Vector2:
        return Vector2.from_angle(self.rotation)

    def translate(self, offset: Vector2) -> None:
        self.position = self.position + offset

    def look_at(self, target: Vector2) -> None:
        self.rotation = self.position.angle_to(target)

    def __repr__(self) -> str:
        return f"Transform2D(pos={self.position}, rot={self.rotation}, scale={self.scale})"
