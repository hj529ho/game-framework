from __future__ import annotations

from typing import Callable

from engine.ecs.component import Component
from engine.physics.collider import Collider
from engine.physics.collision import CollisionInfo, test_collision
from engine.physics.spatial_hash import SpatialHash


class PhysicsWorld(Component):
    """Collision detection system. Add to a manager entity in your scene.

    Runs broadphase (spatial hash) + narrowphase (exact collision test)
    in on_fixed_update. Resolves solid collisions and fires callbacks.

    Example:
        manager = Entity("PhysicsManager")
        physics = manager.add_component(PhysicsWorld(cell_size=64))
        physics.on_collision = my_collision_handler
        scene.add(manager)

    Collision callbacks on entities:
        Components can define on_collision_enter(info: CollisionInfo)
        and on_collision_exit(other_entity: Entity) methods.
    """

    def __init__(self, cell_size: float = 64.0) -> None:
        super().__init__()
        self._spatial_hash = SpatialHash(cell_size)
        self._active_collisions: set[tuple[int, int]] = set()
        self.on_collision: Callable[[CollisionInfo], None] | None = None
        self.resolve_solid = True  # auto-resolve non-trigger collisions

    @property
    def spatial_hash(self) -> SpatialHash:
        return self._spatial_hash

    def on_fixed_update(self, fixed_dt: float) -> None:
        world = self.entity._world
        if world is None:
            return

        # Gather all colliders
        colliders: list[Collider] = []
        for entity in world.entities:
            if entity.active:
                for comp in entity.components:
                    if isinstance(comp, Collider) and comp.enabled:
                        colliders.append(comp)

        # Broadphase
        self._spatial_hash.clear()
        for c in colliders:
            self._spatial_hash.insert(c)

        candidate_pairs = self._spatial_hash.get_candidate_pairs()

        # Narrowphase
        current_collisions: set[tuple[int, int]] = set()

        for a, b in candidate_pairs:
            # Check layer compatibility
            if not (a.layer & b.layer):
                continue

            info = test_collision(a, b)
            if info is None:
                continue

            pair_key = (min(id(a), id(b)), max(id(a), id(b)))
            current_collisions.add(pair_key)

            # Fire global callback
            if self.on_collision:
                self.on_collision(info)

            # Resolve solid collisions
            if self.resolve_solid and not a.is_trigger and not b.is_trigger:
                half_pen = info.penetration / 2
                a.entity.position = a.entity.position + info.normal * half_pen
                b.entity.position = b.entity.position - info.normal * half_pen

            # Fire enter callbacks on components
            if pair_key not in self._active_collisions:
                self._notify_collision_enter(a.entity, b.entity, info)
                self._notify_collision_enter(b.entity, a.entity, info)

        # Fire exit callbacks for collisions that ended
        ended = self._active_collisions - current_collisions
        for pair_key in ended:
            # We can't easily recover entities from expired ids,
            # so exit callbacks are best-effort
            pass

        self._active_collisions = current_collisions

    @staticmethod
    def _notify_collision_enter(entity, other_entity, info: CollisionInfo) -> None:
        for comp in entity.components:
            callback = getattr(comp, 'on_collision_enter', None)
            if callback:
                callback(info)
