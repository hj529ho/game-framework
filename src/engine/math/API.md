# engine.math -- API Reference

## Class: `Vector2`

**File**: `vector2.py`
**Import**: `from engine.math.vector2 import Vector2`

2D vector with `__slots__` for memory efficiency. Supports arithmetic operators, iteration, and indexing.

### Constructor

```python
Vector2(x: float = 0.0, y: float = 0.0)
```

### Fields

| Field | Type | Writable | Description |
|---|---|---|---|
| `x` | `float` | yes | X component |
| `y` | `float` | yes | Y component |

### Operators

| Operator | Right Operand | Returns | Description |
|---|---|---|---|
| `v + w` | `Vector2` | `Vector2` | Component-wise addition |
| `v - w` | `Vector2` | `Vector2` | Component-wise subtraction |
| `v * s` | `float` | `Vector2` | Scalar multiplication |
| `s * v` | `float` (left) | `Vector2` | Scalar multiplication (rmul) |
| `v / s` | `float` | `Vector2` | Scalar division |
| `-v` | -- | `Vector2` | Negation |
| `v == w` | `Vector2` | `bool` | Approximate equality via `math.isclose` |
| `hash(v)` | -- | `int` | Hash of `(x, y)` |
| `v[0]` | `int` | `float` | Index access (0=x, 1=y). Raises `IndexError` for other indices. |
| `iter(v)` | -- | yields `float, float` | Tuple unpacking: `x, y = v` |

### Properties

| Property | Type | Description |
|---|---|---|
| `magnitude` | `float` | Length: `sqrt(x*x + y*y)` |
| `sqr_magnitude` | `float` | Squared length (avoids sqrt) |
| `normalized` | `Vector2` | Unit vector. Returns `Vector2.zero()` if magnitude is 0. |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `dot` | `(other: Vector2)` | `float` | Dot product |
| `cross` | `(other: Vector2)` | `float` | 2D cross product (z-component of 3D cross) |
| `distance_to` | `(other: Vector2)` | `float` | Euclidean distance |
| `angle_to` | `(other: Vector2)` | `float` | Angle in degrees from self to other (via `atan2`) |
| `lerp` | `(other: Vector2, t: float)` | `Vector2` | Linear interpolation. t=0 returns self, t=1 returns other. |
| `rotate` | `(angle_degrees: float)` | `Vector2` | Rotate around origin by given degrees |
| `copy` | `()` | `Vector2` | Returns a new Vector2 with same x, y |

### Static Constructors

| Method | Returns | Value |
|---|---|---|
| `Vector2.zero()` | `Vector2` | `(0, 0)` |
| `Vector2.one()` | `Vector2` | `(1, 1)` |
| `Vector2.up()` | `Vector2` | `(0, -1)` -- screen coordinates: up is negative Y |
| `Vector2.down()` | `Vector2` | `(0, 1)` |
| `Vector2.left()` | `Vector2` | `(-1, 0)` |
| `Vector2.right()` | `Vector2` | `(1, 0)` |
| `Vector2.from_angle(degrees: float)` | `Vector2` | Unit vector at given angle (0=right, 90=down) |

### Usage

```python
pos = Vector2(100, 200)
vel = Vector2.right() * 50.0
pos = pos + vel * dt

dist = pos.distance_to(Vector2.zero())
direction = (target - pos).normalized
```

---

## Class: `Rect`

**File**: `rect.py`
**Import**: `from engine.math.rect import Rect`

Axis-aligned bounding box with `__slots__`.

### Constructor

```python
Rect(x: float, y: float, width: float, height: float)
```

### Fields

| Field | Type | Writable | Description |
|---|---|---|---|
| `x` | `float` | yes | Left edge |
| `y` | `float` | yes | Top edge |
| `width` | `float` | yes | Width |
| `height` | `float` | yes | Height |

### Properties

| Property | Type | Description |
|---|---|---|
| `left` | `float` | `= x` |
| `right` | `float` | `= x + width` |
| `top` | `float` | `= y` |
| `bottom` | `float` | `= y + height` |
| `center` | `Vector2` | Center point of the rectangle |
| `top_left` | `Vector2` | `= (x, y)` |
| `size` | `Vector2` | `= (width, height)` |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `contains_point` | `(point: Vector2)` | `bool` | True if point is inside rect (inclusive edges) |
| `overlaps` | `(other: Rect)` | `bool` | AABB overlap test |
| `intersection` | `(other: Rect)` | `Rect \| None` | Overlapping region, or None if no overlap |
| `expanded` | `(amount: float)` | `Rect` | New rect grown by `amount` on all four sides |
| `to_tuple` | `()` | `tuple[float, float, float, float]` | `(x, y, width, height)` |

---

## Class: `Circle`

**File**: `circle.py`
**Import**: `from engine.math.circle import Circle`

Circle shape with `__slots__`.

### Constructor

```python
Circle(center: Vector2, radius: float)
```

### Fields

| Field | Type | Writable | Description |
|---|---|---|---|
| `center` | `Vector2` | yes | Center position |
| `radius` | `float` | yes | Radius |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `contains_point` | `(point: Vector2)` | `bool` | True if point is inside circle |
| `overlaps_circle` | `(other: Circle)` | `bool` | Circle-circle overlap test |
| `overlaps_rect` | `(rect: Rect)` | `bool` | Circle-AABB overlap test |
| `get_bounds` | `()` | `Rect` | Axis-aligned bounding box of the circle |

---

## Class: `Transform2D`

**File**: `transform.py`
**Import**: `from engine.math.transform import Transform2D`

Position, rotation, and scale container with `__slots__`. Attached to every `Entity`.

### Constructor

```python
Transform2D(
    position: Vector2 | None = None,  # default: Vector2.zero()
    rotation: float = 0.0,            # degrees
    scale: Vector2 | None = None,     # default: Vector2.one()
)
```

### Fields

| Field | Type | Writable | Description |
|---|---|---|---|
| `position` | `Vector2` | yes | World position |
| `rotation` | `float` | yes | Rotation in degrees |
| `scale` | `Vector2` | yes | Scale factor |

### Properties

| Property | Type | Description |
|---|---|---|
| `forward` | `Vector2` | Unit vector in the direction of `rotation` |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `translate` | `(offset: Vector2)` | `None` | Add offset to position |
| `look_at` | `(target: Vector2)` | `None` | Set rotation to face target point |

---

## Module: `utils`

**File**: `utils.py`
**Import**: `from engine.math import utils` or `from engine.math.utils import lerp, clamp, ...`

| Function | Signature | Returns | Description |
|---|---|---|---|
| `lerp` | `(a: float, b: float, t: float)` | `float` | Linear interpolation: `a + (b - a) * t` |
| `clamp` | `(value: float, min_val: float, max_val: float)` | `float` | Clamp value to `[min_val, max_val]` |
| `remap` | `(value: float, from_min: float, from_max: float, to_min: float, to_max: float)` | `float` | Remap value from one range to another |
| `inverse_lerp` | `(a: float, b: float, value: float)` | `float` | Returns t such that `lerp(a, b, t) == value`. Returns 0 if `a == b`. |
| `smoothstep` | `(edge0: float, edge1: float, x: float)` | `float` | Smooth Hermite interpolation between 0 and 1 |

---

## Module: `easing`

**File**: `easing.py`
**Import**: `from engine.math.easing import EASINGS` or individual functions

All easing functions take `t: float` (0.0 to 1.0) and return a `float` (0.0 to 1.0).

### `EASINGS` Dictionary

`EASINGS: dict[str, callable]` maps string names to easing functions. Contains 28 entries.

### All 28 Easing Functions by Name

| Name | Function Signature |
|---|---|
| `"linear"` | `linear(t: float) -> float` |
| `"ease_in_quad"` | `ease_in_quad(t: float) -> float` |
| `"ease_out_quad"` | `ease_out_quad(t: float) -> float` |
| `"ease_in_out_quad"` | `ease_in_out_quad(t: float) -> float` |
| `"ease_in_cubic"` | `ease_in_cubic(t: float) -> float` |
| `"ease_out_cubic"` | `ease_out_cubic(t: float) -> float` |
| `"ease_in_out_cubic"` | `ease_in_out_cubic(t: float) -> float` |
| `"ease_in_quart"` | `ease_in_quart(t: float) -> float` |
| `"ease_out_quart"` | `ease_out_quart(t: float) -> float` |
| `"ease_in_out_quart"` | `ease_in_out_quart(t: float) -> float` |
| `"ease_in_sine"` | `ease_in_sine(t: float) -> float` |
| `"ease_out_sine"` | `ease_out_sine(t: float) -> float` |
| `"ease_in_out_sine"` | `ease_in_out_sine(t: float) -> float` |
| `"ease_in_expo"` | `ease_in_expo(t: float) -> float` |
| `"ease_out_expo"` | `ease_out_expo(t: float) -> float` |
| `"ease_in_out_expo"` | `ease_in_out_expo(t: float) -> float` |
| `"ease_in_circ"` | `ease_in_circ(t: float) -> float` |
| `"ease_out_circ"` | `ease_out_circ(t: float) -> float` |
| `"ease_in_out_circ"` | `ease_in_out_circ(t: float) -> float` |
| `"ease_in_back"` | `ease_in_back(t: float) -> float` |
| `"ease_out_back"` | `ease_out_back(t: float) -> float` |
| `"ease_in_out_back"` | `ease_in_out_back(t: float) -> float` |
| `"ease_in_elastic"` | `ease_in_elastic(t: float) -> float` |
| `"ease_out_elastic"` | `ease_out_elastic(t: float) -> float` |
| `"ease_in_out_elastic"` | `ease_in_out_elastic(t: float) -> float` |
| `"ease_in_bounce"` | `ease_in_bounce(t: float) -> float` |
| `"ease_out_bounce"` | `ease_out_bounce(t: float) -> float` |
| `"ease_in_out_bounce"` | `ease_in_out_bounce(t: float) -> float` |

### Usage

```python
from engine.math.easing import EASINGS, ease_out_back

# By name (for Tween)
tween.set_ease("ease_out_back")

# By function reference
fn = EASINGS["ease_in_out_elastic"]
value = fn(0.5)
```
