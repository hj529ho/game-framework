from __future__ import annotations

from engine.ecs.component import Component
from engine.math.vector2 import Vector2
from engine.math.rect import Rect
from engine.math.circle import Circle


class Collider(Component):
    """Base collider component. Subclass for specific shapes.

    Attributes:
        offset: Local offset from entity position.
        is_trigger: If True, detects overlap but doesn't resolve. Calls on_trigger_enter/exit.
        layer: Collision layer bitmask (default 1). Colliders only interact if layers overlap.
    """

    def __init__(self, offset: Vector2 | None = None, is_trigger: bool = False) -> None:
        super().__init__()
        self.offset = offset or Vector2.zero()
        self.is_trigger = is_trigger
        self.layer: int = 1

    @property
    def world_center(self) -> Vector2:
        """Center position in world space."""
        return self.position + self.offset

    def get_bounds(self) -> Rect:
        """Return axis-aligned bounding box in world space. Override in subclass."""
        raise NotImplementedError


class BoxCollider(Collider):
    """Axis-aligned box collider.

    Example:
        entity.add_component(BoxCollider(40, 40))
    """

    def __init__(
        self,
        width: float,
        height: float,
        offset: Vector2 | None = None,
        is_trigger: bool = False,
    ) -> None:
        super().__init__(offset, is_trigger)
        self.width = width
        self.height = height

    def get_bounds(self) -> Rect:
        c = self.world_center
        return Rect(c.x - self.width / 2, c.y - self.height / 2, self.width, self.height)


class CircleCollider(Collider):
    """Circle collider.

    Example:
        entity.add_component(CircleCollider(20))
    """

    def __init__(
        self,
        radius: float,
        offset: Vector2 | None = None,
        is_trigger: bool = False,
    ) -> None:
        super().__init__(offset, is_trigger)
        self.radius = radius

    def get_bounds(self) -> Rect:
        c = self.world_center
        return Rect(c.x - self.radius, c.y - self.radius, self.radius * 2, self.radius * 2)

    def get_circle(self) -> Circle:
        return Circle(self.world_center, self.radius)
