# engine.math — API Reference

## Class: `Vector2`

**File**: `vector2.py`
**Import**: `from engine.math import Vector2`

2D vector with `__slots__` for memory efficiency. Supports arithmetic operators.

### Constructor

```python
Vector2(x: float = 0.0, y: float = 0.0)
```

### Fields

| Field | Type | Description |
|---|---|---|
| `x` | `float` | X component |
| `y` | `float` | Y component |

### Operators

| Operator | Right Operand | Returns | Description |
|---|---|---|---|
| `+` | `Vector2` | `Vector2` | Component-wise addition |
| `-` | `Vector2` | `Vector2` | Component-wise subtraction |
| `*` | `float` | `Vector2` | Scalar multiplication |
| `float *` | `Vector2` | `Vector2` | Scalar multiplication (rmul) |
| `/` | `float` | `Vector2` | Scalar division |
| `-v` | — | `Vector2` | Negation |
| `==` | `Vector2` | `bool` | Approximate equality (`math.isclose`) |
| `v[0]` | `int` | `float` | Index access (0=x, 1=y) |
| `iter(v)` | — | yields `x`, `y` | Tuple unpacking: `x, y = v` |

### Properties

| Property | Type | Description |
|---|---|---|
| `magnitude` | `float` | Length: `sqrt(x² + y²)` |
| `sqr_magnitude` | `float` | Squared length (avoids sqrt) |
| `normalized` | `Vector2` | Unit vector. Returns `zero()` if magnitude is 0 |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `dot` | `(other: Vector2)` | `float` | Dot product |
| `cross` | `(other: Vector2)` | `float` | 2D cross product (scalar) |
| `distance_to` | `(other: Vector2)` | `float` | Euclidean distance |
| `angle_to` | `(other: Vector2)` | `float` | Angle in degrees to other point |
| `lerp` | `(other: Vector2, t: float)` | `Vector2` | Linear interpolation. t=0→self, t=1→other |
| `rotate` | `(angle_degrees: float)` | `Vector2` | Rotate around origin |
| `copy` | `()` | `Vector2` | Deep copy |

### Static Constructors

| Method | Returns | Value |
|---|---|---|
| `Vector2.zero()` | `Vector2` | `(0, 0)` |
| `Vector2.one()` | `Vector2` | `(1, 1)` |
| `Vector2.up()` | `Vector2` | `(0, -1)` (screen coords) |
| `Vector2.down()` | `Vector2` | `(0, 1)` |
| `Vector2.left()` | `Vector2` | `(-1, 0)` |
| `Vector2.right()` | `Vector2` | `(1, 0)` |
| `Vector2.from_angle(degrees)` | `Vector2` | Unit vector at given angle |

---

## Class: `Rect`

**File**: `rect.py`
**Import**: `from engine.math import Rect`

Axis-aligned bounding box.

### Constructor

```python
Rect(x: float, y: float, width: float, height: float)
```

### Fields

| Field | Type | Description |
|---|---|---|
| `x` | `float` | Left edge |
| `y` | `float` | Top edge |
| `width` | `float` | Width |
| `height` | `float` | Height |

### Properties

| Property | Type | Description |
|---|---|---|
| `left` | `float` | = x |
| `right` | `float` | = x + width |
| `top` | `float` | = y |
| `bottom` | `float` | = y + height |
| `center` | `Vector2` | Center point |
| `top_left` | `Vector2` | = (x, y) |
| `size` | `Vector2` | = (width, height) |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `contains_point` | `(point: Vector2)` | `bool` | Point inside rect (inclusive) |
| `overlaps` | `(other: Rect)` | `bool` | AABB overlap test |
| `intersection` | `(other: Rect)` | `Rect \| None` | Overlapping area, or None |
| `expanded` | `(amount: float)` | `Rect` | Grow by amount on all sides |
| `to_tuple` | `()` | `tuple[float, float, float, float]` | `(x, y, w, h)` |

---

## Class: `Circle`

**File**: `circle.py`
**Import**: `from engine.math import Circle`

### Constructor

```python
Circle(center: Vector2, radius: float)
```

### Fields

| Field | Type |
|---|---|
| `center` | `Vector2` |
| `radius` | `float` |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `contains_point` | `(point: Vector2)` | `bool` | Point inside circle |
| `overlaps_circle` | `(other: Circle)` | `bool` | Circle-circle overlap |
| `overlaps_rect` | `(rect: Rect)` | `bool` | Circle-AABB overlap |
| `get_bounds` | `()` | `Rect` | Bounding AABB |

---

## Class: `Transform2D`

**File**: `transform.py`
**Import**: `from engine.math import Transform2D`

Position, rotation, scale container. Attached to every `Entity`.

### Constructor

```python
Transform2D(
    position: Vector2 | None = None,  # default: Vector2.zero()
    rotation: float = 0.0,            # degrees
    scale: Vector2 | None = None,     # default: Vector2.one()
)
```

### Fields

| Field | Type | Description |
|---|---|---|
| `position` | `Vector2` | World position |
| `rotation` | `float` | Rotation in degrees |
| `scale` | `Vector2` | Scale factor |

### Properties

| Property | Type | Description |
|---|---|---|
| `forward` | `Vector2` | Unit vector in rotation direction |

### Methods

| Method | Signature | Description |
|---|---|---|
| `translate` | `(offset: Vector2) → None` | Add offset to position |
| `look_at` | `(target: Vector2) → None` | Set rotation to face target |

---

## Module: `utils`

**File**: `utils.py`
**Import**: `from engine.math import utils`

| Function | Signature | Returns | Description |
|---|---|---|---|
| `lerp` | `(a: float, b: float, t: float)` | `float` | Linear interpolation |
| `clamp` | `(value, min_val, max_val)` | `float` | Clamp value to range |
| `remap` | `(value, from_min, from_max, to_min, to_max)` | `float` | Remap from one range to another |
| `inverse_lerp` | `(a: float, b: float, value: float)` | `float` | Inverse of lerp: returns t |
| `smoothstep` | `(edge0, edge1, x)` | `float` | Smooth Hermite interpolation |
