# engine.physics -- API Reference

## Class: `Collider` (base)

**File**: `collider.py`
**Import**: `from engine.physics.collider import Collider`
**Inherits**: `Component`

Base collider component. Do not use directly -- use `BoxCollider` or `CircleCollider`.

### Constructor

```python
Collider(offset: Vector2 | None = None, is_trigger: bool = False)
```

### Properties / Fields

| Name | Type | Writable | Description |
|---|---|---|---|
| `offset` | `Vector2` | yes | Local offset from entity position. Default: `Vector2.zero()`. |
| `is_trigger` | `bool` | yes | If `True`, detects overlap but does not resolve. Default: `False`. |
| `layer` | `int` | yes | Collision layer bitmask. Default: `1`. Colliders interact only if `a.layer & b.layer` is truthy. |
| `world_center` | `Vector2` | no | Computed: `entity.position + offset` |

### Abstract Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `get_bounds` | `()` | `Rect` | World-space axis-aligned bounding box. Must be overridden. |

---

## Class: `BoxCollider`

**File**: `collider.py`
**Import**: `from engine.physics.collider import BoxCollider`
**Inherits**: `Collider`

Axis-aligned box collider.

### Constructor

```python
BoxCollider(
    width: float,
    height: float,
    offset: Vector2 | None = None,
    is_trigger: bool = False,
)
```

### Fields

| Field | Type | Writable | Description |
|---|---|---|---|
| `width` | `float` | yes | Box width |
| `height` | `float` | yes | Box height |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `get_bounds` | `()` | `Rect` | AABB centered on `world_center` with `width` x `height` |

### Usage

```python
entity.add_component(BoxCollider(40, 40))
entity.add_component(BoxCollider(60, 20, offset=Vector2(0, 30), is_trigger=True))
```

---

## Class: `CircleCollider`

**File**: `collider.py`
**Import**: `from engine.physics.collider import CircleCollider`
**Inherits**: `Collider`

Circle collider.

### Constructor

```python
CircleCollider(
    radius: float,
    offset: Vector2 | None = None,
    is_trigger: bool = False,
)
```

### Fields

| Field | Type | Writable | Description |
|---|---|---|---|
| `radius` | `float` | yes | Circle radius |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `get_bounds` | `()` | `Rect` | AABB centered on `world_center` with side `2 * radius` |
| `get_circle` | `()` | `Circle` | Returns `Circle(world_center, radius)` |

---

## Dataclass: `CollisionInfo`

**File**: `collision.py`
**Import**: `from engine.physics.collision import CollisionInfo`

Result of a narrowphase collision test between two colliders.

| Field | Type | Description |
|---|---|---|
| `collider_a` | `Collider` | First collider |
| `collider_b` | `Collider` | Second collider |
| `normal` | `Vector2` | Push direction: pushes A away from B |
| `penetration` | `float` | Overlap depth |
| `contact_point` | `Vector2` | Approximate contact point |

---

## Dataclass: `RaycastHit`

**File**: `collision.py`
**Import**: `from engine.physics.collision import RaycastHit`

Result of a raycast.

| Field | Type | Description |
|---|---|---|
| `collider` | `Collider` | The collider that was hit |
| `point` | `Vector2` | World-space hit point |
| `normal` | `Vector2` | Surface normal at hit point |
| `distance` | `float` | Distance from ray origin to hit point |

---

## Function: `test_collision`

**File**: `collision.py`
**Import**: `from engine.physics.collision import test_collision`

```python
test_collision(a: Collider, b: Collider) -> CollisionInfo | None
```

Test collision between any two colliders. Supports all combinations:
- `BoxCollider` vs `BoxCollider` (AABB overlap + minimum penetration axis)
- `CircleCollider` vs `CircleCollider` (distance check)
- `BoxCollider` vs `CircleCollider` (closest point on AABB)
- `CircleCollider` vs `BoxCollider` (reversed, normal flipped)

Returns `CollisionInfo` if overlapping, otherwise `None`.

---

## Function: `raycast`

**File**: `collision.py`
**Import**: `from engine.physics.collision import raycast`

```python
raycast(
    origin: Vector2,
    direction: Vector2,
    colliders: list[Collider],
    max_distance: float = float('inf'),
    layer_mask: int = 0xFFFFFFFF,
) -> RaycastHit | None
```

Cast a ray and return the **closest** hit, or `None`.

| Parameter | Type | Description |
|---|---|---|
| `origin` | `Vector2` | Ray start point in world space |
| `direction` | `Vector2` | Ray direction (auto-normalized internally) |
| `colliders` | `list[Collider]` | Colliders to test against |
| `max_distance` | `float` | Maximum ray length. Default: infinite. |
| `layer_mask` | `int` | Bitmask. Only tests colliders where `collider.layer & mask` is truthy. Default: all bits set. |

Uses slab method for AABB intersection and quadratic formula for circle intersection.

---

## Function: `raycast_all`

**File**: `collision.py`
**Import**: `from engine.physics.collision import raycast_all`

```python
raycast_all(
    origin: Vector2,
    direction: Vector2,
    colliders: list[Collider],
    max_distance: float = float('inf'),
    layer_mask: int = 0xFFFFFFFF,
) -> list[RaycastHit]
```

Cast a ray and return **all** hits sorted by distance (nearest first). Same parameters as `raycast`.

---

## Class: `SpatialHash`

**File**: `spatial_hash.py`
**Import**: `from engine.physics.spatial_hash import SpatialHash`

Grid-based broadphase collision detection. Divides the world into cells; each collider is inserted into all cells its AABB overlaps.

### Constructor

```python
SpatialHash(cell_size: float = 64.0)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `cell_size` | `float` | no | Grid cell size in world units |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `clear` | `()` | `None` | Clear all cells |
| `insert` | `(collider: Collider)` | `None` | Insert collider into all overlapping cells |
| `query` | `(collider: Collider)` | `list[Collider]` | Get all other colliders sharing cells with this one (deduplicated) |
| `get_candidate_pairs` | `()` | `list[tuple[Collider, Collider]]` | All unique pairs of colliders sharing at least one cell |

---

## Class: `PhysicsWorld`

**File**: `physics_world.py`
**Import**: `from engine.physics.physics_world import PhysicsWorld`
**Inherits**: `Component`

Collision detection system. Add to a manager entity in your scene. Runs broadphase (spatial hash) + narrowphase (exact collision test) in `on_fixed_update`.

### Constructor

```python
PhysicsWorld(cell_size: float = 64.0)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `spatial_hash` | `SpatialHash` | no | The broadphase grid |
| `on_collision` | `Callable[[CollisionInfo], None] \| None` | yes | Global collision callback. Called for every collision. Default: `None`. |
| `resolve_solid` | `bool` | yes | If `True` (default), auto-resolve non-trigger collisions by pushing entities apart by `penetration / 2` along normal. |

### How It Works (each `on_fixed_update`)

1. Gather all active `Collider` components from all active entities in the world.
2. Insert into spatial hash (broadphase).
3. Test all candidate pairs (narrowphase) -- only if `a.layer & b.layer`.
4. For each collision:
   - Call `on_collision` global callback (if set).
   - If `resolve_solid` and neither collider is a trigger: push entities apart.
   - If this is a new collision pair: call `on_collision_enter(info)` on all components of both entities.
5. Track active collision pairs for enter/exit detection.

### Collision Callbacks on Components

Define `on_collision_enter` on any Component to receive notifications:

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
