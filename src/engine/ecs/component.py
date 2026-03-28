from __future__ import annotations

from typing import TYPE_CHECKING

from engine.core.lifecycle import Lifecycle

if TYPE_CHECKING:
    from engine.ecs.entity import Entity
    from engine.math.vector2 import Vector2
    from engine.math.transform import Transform2D


class Component(Lifecycle):
    """Base component class. Inherit and override lifecycle hooks.

    Attach to an Entity to give it behavior. Like Unity's MonoBehaviour.

    Example:
        class PlayerMovement(Component):
            def on_start(self):
                self.speed = 200.0

            def on_update(self, dt):
                if self.entity.game.keyboard.is_pressed(Key.RIGHT):
                    self.transform.translate(Vector2.right() * self.speed * dt)

        player = Entity("Player")
        player.add_component(PlayerMovement())
        scene.add(player)
    """

    def __init__(self) -> None:
        self._entity: Entity | None = None
        self._started = False
        self._enabled = True

    @property
    def entity(self) -> Entity:
        """The Entity this component is attached to."""
        if self._entity is None:
            raise RuntimeError("Component is not attached to any entity.")
        return self._entity

    @property
    def transform(self) -> Transform2D:
        """Shortcut for self.entity.transform."""
        return self.entity.transform

    @property
    def position(self) -> Vector2:
        """Shortcut for self.entity.position."""
        return self.entity.position

    @position.setter
    def position(self, value: Vector2) -> None:
        self.entity.position = value

    @property
    def enabled(self) -> bool:
        """If False, on_update/on_late_update/on_draw are skipped."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value
