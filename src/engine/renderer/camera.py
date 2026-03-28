from __future__ import annotations

from engine.ecs.component import Component
from engine.math.vector2 import Vector2
from engine.math.rect import Rect
from engine.math import utils


class Camera2D(Component):
    """2D camera component. Attach to an entity to make it the active camera.

    The camera's position is the entity's position (center of view).
    Renderer uses the active camera to transform world -> screen coordinates.

    Example:
        cam_entity = Entity("Camera")
        cam_entity.position = Vector2(400, 300)
        camera = cam_entity.add_component(Camera2D(800, 600))
        camera.follow_target = player_entity
        scene.add(cam_entity)
    """

    # Class-level active camera reference
    _active: Camera2D | None = None

    def __init__(self, viewport_width: int = 800, viewport_height: int = 600) -> None:
        super().__init__()
        self._viewport_w = viewport_width
        self._viewport_h = viewport_height
        self.zoom: float = 1.0
        self.follow_target = None  # Entity to follow
        self.follow_speed: float = 5.0  # lerp speed (0 = instant)
        self.follow_offset = Vector2.zero()

    def on_awake(self) -> None:
        if Camera2D._active is None:
            Camera2D._active = self

    def on_destroy(self) -> None:
        if Camera2D._active is self:
            Camera2D._active = None

    @staticmethod
    def get_active() -> Camera2D | None:
        return Camera2D._active

    def set_active(self) -> None:
        Camera2D._active = self

    @property
    def viewport_width(self) -> int:
        return self._viewport_w

    @property
    def viewport_height(self) -> int:
        return self._viewport_h

    def on_late_update(self, dt: float) -> None:
        if self.follow_target is not None:
            target_pos = self.follow_target.position + self.follow_offset
            if self.follow_speed <= 0:
                self.position = target_pos
            else:
                t = min(1.0, self.follow_speed * dt)
                self.position = self.position.lerp(target_pos, t)

    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """Convert world coordinates to screen coordinates."""
        cam_pos = self.position
        sx = (world_pos.x - cam_pos.x) * self.zoom + self._viewport_w / 2
        sy = (world_pos.y - cam_pos.y) * self.zoom + self._viewport_h / 2
        return Vector2(sx, sy)

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """Convert screen coordinates to world coordinates."""
        cam_pos = self.position
        wx = (screen_pos.x - self._viewport_w / 2) / self.zoom + cam_pos.x
        wy = (screen_pos.y - self._viewport_h / 2) / self.zoom + cam_pos.y
        return Vector2(wx, wy)

    @property
    def bounds(self) -> Rect:
        """Visible world-space rectangle (for culling)."""
        half_w = (self._viewport_w / 2) / self.zoom
        half_h = (self._viewport_h / 2) / self.zoom
        cam_pos = self.position
        return Rect(cam_pos.x - half_w, cam_pos.y - half_h, half_w * 2, half_h * 2)
