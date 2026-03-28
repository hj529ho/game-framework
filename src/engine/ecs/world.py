from __future__ import annotations

from typing import TypeVar, TYPE_CHECKING

from engine.ecs.entity import Entity
from engine.ecs.component import Component

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer

T = TypeVar("T", bound=Entity)


class World:
    """Container for entities. Manages lifecycle hook dispatch.

    Lifecycle order per frame:
        1. Process pending additions (add queued entities, call on_start on new components)
        2. on_fixed_update(fixed_dt) — 0~N times, fixed timestep accumulator
        3. on_update(dt) on all active entity components
        4. on_late_update(dt) on all active entity components
        5. Process pending removals (call on_destroy, remove entities)

    Draw phase (separate from update):
        on_draw(renderer) on all active entity components
    """

    def __init__(self, fixed_timestep: float = 1.0 / 50.0) -> None:
        self._entities: list[Entity] = []
        self._to_add: list[Entity] = []
        self._to_remove: list[Entity] = []
        self._fixed_timestep = fixed_timestep
        self._fixed_accumulator: float = 0.0

    def add(self, entity: Entity) -> Entity:
        """Queue entity for addition. Actual add happens in next update()."""
        self._to_add.append(entity)
        return entity

    def remove(self, entity: Entity) -> None:
        """Queue entity for removal. Actual remove happens in next update()."""
        self._to_remove.append(entity)

    def _process_additions(self) -> None:
        for entity in self._to_add:
            if entity not in self._entities:
                entity._world = self
                self._entities.append(entity)
        self._to_add.clear()

    def _process_removals(self) -> None:
        for entity in self._to_remove:
            if entity in self._entities:
                entity._destroy_components()
                entity._world = None
                self._entities.remove(entity)
        self._to_remove.clear()

    @property
    def fixed_timestep(self) -> float:
        return self._fixed_timestep

    @fixed_timestep.setter
    def fixed_timestep(self, value: float) -> None:
        self._fixed_timestep = value

    def update(self, dt: float) -> None:
        """Full update cycle: additions → start → fixed_update → update → late_update → removals."""
        # 1. Process pending additions
        self._process_additions()

        # 2. Start components that haven't started yet
        for entity in self._entities:
            if entity.active:
                entity._start_components()

        # 3. Fixed update (accumulator-based, may run 0~N times)
        self._fixed_accumulator += dt
        while self._fixed_accumulator >= self._fixed_timestep:
            for entity in self._entities:
                if entity.active:
                    entity._fixed_update_components(self._fixed_timestep)
            self._fixed_accumulator -= self._fixed_timestep

        # 4. Update
        for entity in self._entities:
            if entity.active:
                entity._update_components(dt)

        # 5. Late update
        for entity in self._entities:
            if entity.active:
                entity._late_update_components(dt)

        # 6. Process pending removals
        self._process_removals()

    def draw(self, renderer: Renderer) -> None:
        """Call on_draw on all active entity components."""
        for entity in self._entities:
            if entity.active:
                entity._draw_components(renderer)

    def clear(self) -> None:
        """Immediately remove all entities, destroying their components."""
        for entity in self._entities:
            entity._destroy_components()
            entity._world = None
        self._entities.clear()
        self._to_add.clear()
        self._to_remove.clear()

    # --- Queries ---

    def find_by_name(self, name: str) -> Entity | None:
        for entity in self._entities:
            if entity.name == name:
                return entity
        return None

    def find_by_tag(self, tag: str) -> list[Entity]:
        return [e for e in self._entities if e.has_tag(tag)]

    def find_by_type(self, entity_type: type[T]) -> list[T]:
        return [e for e in self._entities if isinstance(e, entity_type)]

    def find_with_component(self, *comp_types: type[Component]) -> list[Entity]:
        """Find all entities that have ALL given component types."""
        return [
            e for e in self._entities
            if all(e.has_component(ct) for ct in comp_types)
        ]

    @property
    def entities(self) -> list[Entity]:
        return self._entities.copy()

    def __len__(self) -> int:
        return len(self._entities)
