# engine.physics -- API Reference

## Class: `Collider` (base)

**File**: `collider.py`
**Inherits**: `Component`

Base collider component. Do not use directly — use BoxCollider or CircleCollider.

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `offset` | `Vector2` | yes | Local offset from entity position |
| `is_trigger` | `bool` | yes | If True, detects overlap but does not resolve |
| `layer` | `int` | yes | Collision layer bitmask (default 1). Colliders interact only if `a.layer & b.layer` is truthy. |
| `world_center` | `Vector2` | no | `entity.position + offset` |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `get_bounds` | `()` | `Rect` | World-space AABB. Override in subclass. |

---

## Class: `BoxCollider`

**Inherits**: `Collider`

Axis-aligned box collider.

### Constructor

```python
BoxCollider(width: float, height: float, offset: Vector2 | None = None, is_trigger: bool = False)
```

### Fields

| Field | Type | Description |
|---|---|---|
| `width` | `float` | Box width |
| `height` | `float` | Box height |

---

## Class: `CircleCollider`

**Inherits**: `Collider`

Circle collider.

### Constructor

```python
CircleCollider(radius: float, offset: Vector2 | None = None, is_trigger: bool = False)
```

### Fields / Methods

| Name | Type | Description |
|---|---|---|
| `radius` | `float` | Circle radius |
| `get_circle()` | `Circle` | Returns `Circle(world_center, radius)` |

---

## Dataclass: `CollisionInfo`

**File**: `collision.py`

Result of a narrowphase collision test.

| Field | Type | Description |
|---|---|---|
| `collider_a` | `Collider` | First collider |
| `collider_b` | `Collider` | Second collider |
| `normal` | `Vector2` | Push direction (pushes A away from B) |
| `penetration` | `float` | Overlap depth |
| `contact_point` | `Vector2` | Approximate contact point |

---

## Dataclass: `RaycastHit`

**File**: `collision.py`

Result of a raycast.

| Field | Type | Description |
|---|---|---|
| `collider` | `Collider` | The collider that was hit |
| `point` | `Vector2` | World-space hit point |
| `normal` | `Vector2` | Surface normal at hit point |
| `distance` | `float` | Distance from ray origin to hit point |

---

## Function: `test_collision`

```python
test_collision(a: Collider, b: Collider) -> CollisionInfo | None
```

Test collision between any two colliders. Supports: Box-Box, Circle-Circle, Box-Circle. Returns None if no collision.

---

## Function: `raycast`

```python
raycast(
    origin: Vector2,
    direction: Vector2,
    colliders: list[Collider],
    max_distance: float = inf,
    layer_mask: int = 0xFFFFFFFF,
) -> RaycastHit | None
```

Cast a ray and return the **closest** hit, or None. Uses slab method for AABB, quadratic formula for circles.

| Parameter | Description |
|---|---|
| `origin` | Ray start point (world space) |
| `direction` | Ray direction (auto-normalized) |
| `colliders` | Colliders to test against |
| `max_distance` | Maximum ray length (default: infinite) |
| `layer_mask` | Only test colliders where `collider.layer & mask` is truthy |

---

## Function: `raycast_all`

```python
raycast_all(
    origin: Vector2,
    direction: Vector2,
    colliders: list[Collider],
    max_distance: float = inf,
    layer_mask: int = 0xFFFFFFFF,
) -> list[RaycastHit]
```

Cast a ray and return **all** hits sorted by distance (nearest first).

### Raycast Usage

```python
class ShootComponent(Component):
    def on_update(self, dt):
        if current_app().keyboard.is_just_pressed(Key.SPACE):
            # Gather colliders from the world
            world = self.entity._world
            colliders = []
            for e in world.entities:
                for c in e.components:
                    if isinstance(c, Collider) and c.entity is not self.entity:
                        colliders.append(c)

            hit = raycast(self.position, Vector2.right(), colliders, max_distance=500)
            if hit:
                print(f"Hit {hit.collider.entity.name} at {hit.point}")
```

---

## Class: `SpatialHash`

**File**: `spatial_hash.py`

Grid-based broadphase. Divides world into cells, returns candidate pairs.

### Constructor

```python
SpatialHash(cell_size: float = 64.0)
```

### Methods

| Method | Signature | Description |
|---|---|---|
| `clear` | `()` | Clear all cells |
| `insert` | `(collider: Collider)` | Insert collider into overlapping cells |
| `query` | `(collider: Collider) -> list[Collider]` | Get all other colliders sharing cells |
| `get_candidate_pairs` | `() -> list[tuple[Collider, Collider]]` | All unique overlapping pairs |

---

## Class: `PhysicsWorld`

**File**: `physics_world.py`
**Inherits**: `Component`

Collision detection system. Add to a manager entity in your scene.
Runs in `on_fixed_update`: broadphase (spatial hash) then narrowphase (exact test).

### Constructor

```python
PhysicsWorld(cell_size: float = 64.0)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `spatial_hash` | `SpatialHash` | no | The broadphase grid |
| `on_collision` | `Callable[[CollisionInfo], None] \| None` | yes | Global collision callback |
| `resolve_solid` | `bool` | yes | If True (default), auto-resolve non-trigger overlaps |

### How It Works

Each `on_fixed_update`:
1. Gathers all active `Collider` components in the world
2. Inserts into spatial hash (broadphase)
3. Tests candidate pairs (narrowphase)
4. For solid colliders: pushes entities apart by `penetration / 2`
5. Calls `on_collision_enter(info)` on entity components for new collisions

### Collision Callbacks on Components

Define these methods on any Component to receive collision notifications:

```python
class PlayerHit(Component):
    def on_collision_enter(self, info: CollisionInfo):
        other = info.collider_b.entity if info.collider_a.entity is self.entity else info.collider_a.entity
        print(f"Collided with {other.name}")
```

### Usage

```python
class GameScene(Scene):
    def on_enter(self):
        # Physics manager
        mgr = Entity("Physics")
        mgr.add_component(PhysicsWorld(cell_size=64))
        self.add(mgr)

        # Player with collider
        player = Entity("Player")
        player.add_component(BoxCollider(40, 40))
        player.add_component(PlayerMovement())
        self.add(player)

        # Wall
        wall = Entity("Wall")
        wall.position = Vector2(300, 300)
        wall.add_component(BoxCollider(100, 100))
        self.add(wall)
```
