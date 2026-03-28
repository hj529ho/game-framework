from __future__ import annotations

from typing import TypeVar, TYPE_CHECKING

from engine.math.vector2 import Vector2
from engine.math.transform import Transform2D
from engine.ecs.component import Component

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer
    from engine.ecs.world import World
    from engine.core.game import Game

T = TypeVar("T", bound=Component)


class Entity:
    """Game object container. Like Unity's GameObject.

    Entity itself has no behavior — all logic goes in Components.
    Entity provides a Transform and manages its attached Components.

    Example:
        player = Entity("Player")
        player.position = Vector2(400, 300)
        player.add_component(PlayerMovement())
        player.add_component(SpriteRenderer())
        scene.add(player)
    """

    _next_id: int = 0

    def __init__(self, name: str = "") -> None:
        Entity._next_id += 1
        self._id = Entity._next_id
        self._name = name or f"Entity_{self._id}"
        self._transform = Transform2D()
        self._components: list[Component] = []
        self._tags: set[str] = set()
        self._active = True
        self._world: World | None = None
        self._parent: Entity | None = None
        self._children: list[Entity] = []

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    # --- Transform shortcuts ---

    @property
    def transform(self) -> Transform2D:
        return self._transform

    @property
    def position(self) -> Vector2:
        return self._transform.position

    @position.setter
    def position(self, value: Vector2) -> None:
        self._transform.position = value

    @property
    def rotation(self) -> float:
        return self._transform.rotation

    @rotation.setter
    def rotation(self, value: float) -> None:
        self._transform.rotation = value

    @property
    def scale(self) -> Vector2:
        return self._transform.scale

    @scale.setter
    def scale(self, value: Vector2) -> None:
        self._transform.scale = value

    # --- Component management ---

    def add_component(self, component: T) -> T:
        """Attach a component. Calls component.on_awake()."""
        if component._entity is not None:
            raise ValueError(
                f"Component {type(component).__name__} is already attached to "
                f"'{component._entity.name}'."
            )
        self._components.append(component)
        component._entity = self
        component.on_awake()
        return component

    def get_component(self, comp_type: type[T]) -> T | None:
        """Get the first component matching the type."""
        for c in self._components:
            if isinstance(c, comp_type):
                return c
        return None

    def get_components(self, comp_type: type[T]) -> list[T]:
        """Get all components matching the type."""
        return [c for c in self._components if isinstance(c, comp_type)]

    def has_component(self, comp_type: type[Component]) -> bool:
        return any(isinstance(c, comp_type) for c in self._components)

    def remove_component(self, component: Component) -> None:
        """Remove a specific component instance. Calls component.on_destroy()."""
        if component in self._components:
            component.on_destroy()
            self._components.remove(component)
            component._entity = None

    def remove_components(self, comp_type: type[Component]) -> None:
        """Remove all components of a given type."""
        to_remove = [c for c in self._components if isinstance(c, comp_type)]
        for c in to_remove:
            self.remove_component(c)

    @property
    def components(self) -> list[Component]:
        return self._components.copy()

    # --- Tags ---

    @property
    def tags(self) -> set[str]:
        return self._tags

    def add_tag(self, tag: str) -> None:
        self._tags.add(tag)

    def has_tag(self, tag: str) -> bool:
        return tag in self._tags

    # --- Hierarchy ---

    @property
    def parent(self) -> Entity | None:
        return self._parent

    @property
    def children(self) -> list[Entity]:
        return self._children.copy()

    def add_child(self, child: Entity) -> None:
        if child._parent is not None:
            child._parent._children.remove(child)
        child._parent = self
        self._children.append(child)
        if self._world and child._world is None:
            self._world.add(child)

    def remove_child(self, child: Entity) -> None:
        if child in self._children:
            self._children.remove(child)
            child._parent = None

    # --- State ---

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        self._active = value

    # --- Internal lifecycle (called by World) ---

    def _start_components(self) -> None:
        """Call on_start on components that haven't started yet."""
        for comp in self._components:
            if comp.enabled and not comp._started:
                comp.on_start()
                comp._started = True

    def _fixed_update_components(self, fixed_dt: float) -> None:
        for comp in self._components:
            if comp.enabled:
                comp.on_fixed_update(fixed_dt)

    def _update_components(self, dt: float) -> None:
        for comp in self._components:
            if comp.enabled:
                comp.on_update(dt)

    def _late_update_components(self, dt: float) -> None:
        for comp in self._components:
            if comp.enabled:
                comp.on_late_update(dt)

    def _draw_components(self, renderer: Renderer) -> None:
        for comp in self._components:
            if comp.enabled:
                comp.on_draw(renderer)

    def _destroy_components(self) -> None:
        for comp in self._components:
            comp.on_destroy()
            comp._entity = None
        self._components.clear()

    def __repr__(self) -> str:
        comp_names = [type(c).__name__ for c in self._components]
        return f"<Entity '{self._name}' components={comp_names}>"
