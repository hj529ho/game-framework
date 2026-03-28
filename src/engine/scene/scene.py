from __future__ import annotations

from typing import TypeVar, TYPE_CHECKING

from engine.ecs.entity import Entity
from engine.ecs.component import Component
from engine.ecs.world import World

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer

T = TypeVar("T", bound=Component)


class Scene:
    """Game scene. Owns a World of entities.

    Override on_enter/on_exit for scene-level setup/teardown.
    Entity behavior is defined in Components, not in Scene.

    Example:
        class GameScene(Scene):
            def on_enter(self):
                player = Entity("Player")
                player.position = Vector2(400, 300)
                player.add_component(PlayerMovement())
                player.add_component(SpriteRenderer())
                self.add(player)

            def on_exit(self):
                self.world.clear()
    """

    def __init__(self, name: str = "") -> None:
        self._name = name or type(self).__name__
        self._world = World()

    @property
    def name(self) -> str:
        return self._name

    @property
    def world(self) -> World:
        return self._world

    # --- Entity convenience ---

    def add(self, entity: Entity) -> Entity:
        return self._world.add(entity)

    def remove(self, entity: Entity) -> None:
        self._world.remove(entity)

    def find(self, name: str) -> Entity | None:
        return self._world.find_by_name(name)

    def find_by_tag(self, tag: str) -> list[Entity]:
        return self._world.find_by_tag(tag)

    def find_with_component(self, *comp_types: type[T]) -> list[Entity]:
        return self._world.find_with_component(*comp_types)

    # --- Scene lifecycle hooks (override in subclass) ---

    def on_enter(self) -> None:
        """Called when this scene becomes active."""
        pass

    def on_exit(self) -> None:
        """Called when this scene is removed."""
        pass

    def on_pause(self) -> None:
        """Called when another scene is pushed on top."""
        pass

    def on_resume(self) -> None:
        """Called when the scene above is popped."""
        pass

    # --- Frame methods (called by SceneManager) ---

    def update(self, dt: float) -> None:
        self._world.update(dt)

    def draw(self, renderer: Renderer) -> None:
        self._world.draw(renderer)
