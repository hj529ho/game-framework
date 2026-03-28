# Math Module

The `engine.math` module provides 2D math primitives and utility functions used
throughout the engine and your game code. Everything here is pure Python with no
SDL2 dependency (except that `Vector2` and friends are used by SDL2-backed
classes elsewhere).

---

## Vector2

`Vector2` is a 2D vector with `x` and `y` components. It is used for positions,
velocities, directions, sizes, and any other two-component value. It uses
`__slots__` for memory efficiency.

### Creating vectors

```python
from engine import Vector2

# From components
v = Vector2(3.0, 4.0)

# Default is (0, 0)
origin = Vector2()

# Named constructors
zero  = Vector2.zero()       # (0, 0)
one   = Vector2.one()        # (1, 1)
up    = Vector2.up()         # (0, -1)  -- screen coordinates: Y points down
down  = Vector2.down()       # (0, 1)
left  = Vector2.left()       # (-1, 0)
right = Vector2.right()      # (1, 0)

# From angle (degrees, 0 = right, 90 = down in screen coords)
direction = Vector2.from_angle(45)  # approximately (0.707, 0.707)
```

**Important**: Screen coordinates have the Y axis pointing **downward**. This is
why `Vector2.up()` returns `(0, -1)` -- moving "up" on screen means decreasing
Y.

```
Screen coordinate system:

(0,0) -----> +X
  |
  |
  v
  +Y
```

### Arithmetic operators

All arithmetic operators return new `Vector2` instances. The originals are never
modified.

```python
a = Vector2(1, 2)
b = Vector2(3, 4)

# Addition and subtraction
c = a + b        # Vector2(4, 6)
d = a - b        # Vector2(-2, -2)

# Scalar multiplication and division
e = a * 3        # Vector2(3, 6)
f = 3 * a        # Vector2(3, 6)  -- works both ways
g = a / 2        # Vector2(0.5, 1.0)

# Negation
h = -a           # Vector2(-1, -2)
```

### Properties

```python
v = Vector2(3, 4)

v.magnitude       # 5.0  -- the length: sqrt(3^2 + 4^2)
v.sqr_magnitude   # 25.0 -- squared length (faster, no sqrt)
v.normalized      # Vector2(0.6, 0.8) -- unit vector (length 1)
```

Use `sqr_magnitude` when comparing distances to avoid the cost of the square
root:

```python
# Instead of:
if bullet_pos.distance_to(enemy_pos) < 50:

# Use (faster):
diff = bullet_pos - enemy_pos
if diff.sqr_magnitude < 50 * 50:
```

### Methods

#### `dot(other)` -- Dot product

Returns a scalar. Useful for projections and determining if two vectors point in
similar directions.

```python
a = Vector2(1, 0)
b = Vector2(0, 1)

a.dot(b)   # 0.0  -- perpendicular
a.dot(a)   # 1.0  -- parallel (same direction)
a.dot(-a)  # -1.0 -- opposite directions
```

```
Dot product interpretation:
  > 0 : vectors point in roughly the same direction
  = 0 : vectors are perpendicular
  < 0 : vectors point in roughly opposite directions
```

#### `cross(other)` -- 2D cross product

Returns a scalar representing the signed area of the parallelogram formed by the
two vectors. Useful for determining "left of" or "right of" relationships.

```python
a = Vector2(1, 0)
b = Vector2(0, 1)

a.cross(b)   #  1.0 -- b is to the left of a (counterclockwise)
b.cross(a)   # -1.0 -- a is to the right of b (clockwise)
```

#### `distance_to(other)` -- Euclidean distance

```python
a = Vector2(0, 0)
b = Vector2(3, 4)

a.distance_to(b)  # 5.0
```

#### `angle_to(other)` -- Angle in degrees

Returns the angle from this point to another point, in degrees. Uses
`atan2(dy, dx)`.

```python
origin = Vector2(0, 0)
target = Vector2(1, 0)

origin.angle_to(target)  # 0.0 (pointing right)
```

#### `lerp(other, t)` -- Linear interpolation

Returns a point between `self` and `other`. `t=0` returns `self`, `t=1` returns
`other`, `t=0.5` returns the midpoint.

```python
a = Vector2(0, 0)
b = Vector2(100, 200)

a.lerp(b, 0.0)   # Vector2(0, 0)
a.lerp(b, 0.5)   # Vector2(50, 100)
a.lerp(b, 1.0)   # Vector2(100, 200)
a.lerp(b, 0.25)  # Vector2(25, 50)
```

```
  a --------*-----------*-----------*----------- b
  t=0      t=0.25      t=0.5      t=0.75       t=1
```

This is commonly used for smooth movement, camera following, and animations.

#### `rotate(angle_degrees)` -- Rotate around origin

Returns a new vector rotated by the given angle around (0, 0).

```python
v = Vector2(1, 0)
v.rotate(90)   # approximately Vector2(0, 1)
v.rotate(180)  # approximately Vector2(-1, 0)
v.rotate(-45)  # approximately Vector2(0.707, -0.707)
```

#### `copy()` -- Deep copy

```python
a = Vector2(3, 4)
b = a.copy()   # independent copy
b.x = 99       # does not affect a
```

### Indexing and unpacking

```python
v = Vector2(3, 4)

v[0]       # 3.0
v[1]       # 4.0

x, y = v   # tuple unpacking
```

### Equality

Equality uses `math.isclose` for floating-point tolerance:

```python
Vector2(1.0, 2.0) == Vector2(1.0, 2.0)          # True
Vector2(1.0, 2.0) == Vector2(1.0000001, 2.0)    # True (within tolerance)
Vector2(1.0, 2.0) == Vector2(1.1, 2.0)          # False
```

---

## Rect

`Rect` represents an axis-aligned bounding box (AABB). It is defined by its
top-left corner `(x, y)` and its `width` and `height`.

### Creating rectangles

```python
from engine import Rect

# A 100x50 rectangle at position (200, 150)
r = Rect(200, 150, 100, 50)
```

```
  (x, y) = (200, 150)
     +------------------+
     |                  |  height = 50
     |                  |
     +------------------+
          width = 100
```

### Edge and corner properties

```python
r = Rect(200, 150, 100, 50)

r.left       # 200.0       (= x)
r.right      # 300.0       (= x + width)
r.top        # 150.0       (= y)
r.bottom     # 200.0       (= y + height)
r.center     # Vector2(250, 175)
r.top_left   # Vector2(200, 150)
r.size       # Vector2(100, 50)
```

### Collision detection

#### `contains_point(point)` -- Is a point inside?

```python
r = Rect(100, 100, 200, 200)

r.contains_point(Vector2(150, 150))  # True  -- inside
r.contains_point(Vector2(100, 100))  # True  -- on the edge (inclusive)
r.contains_point(Vector2(50, 150))   # False -- outside
```

#### `overlaps(other)` -- AABB overlap test

```python
a = Rect(0, 0, 100, 100)
b = Rect(50, 50, 100, 100)
c = Rect(200, 200, 50, 50)

a.overlaps(b)  # True  -- they overlap
a.overlaps(c)  # False -- no overlap
```

```
  +-------+
  |   a   |
  |   +---+---+
  +---+---+   |
      |   b   |
      +-------+

  a.overlaps(b) = True
```

#### `intersection(other)` -- Overlapping area

Returns a new `Rect` representing the overlapping area, or `None` if there is no
overlap.

```python
a = Rect(0, 0, 100, 100)
b = Rect(50, 50, 100, 100)

overlap = a.intersection(b)  # Rect(50, 50, 50, 50)
```

#### `expanded(amount)` -- Grow on all sides

```python
r = Rect(100, 100, 50, 50)
bigger = r.expanded(10)  # Rect(90, 90, 70, 70)
```

```
  +--expanded (amount=10)--+
  |  +---original---+      |
  |  |              |      |
  |  +--------------+      |
  +------------------------+
```

#### `to_tuple()` -- Convert to tuple

```python
r = Rect(10, 20, 30, 40)
r.to_tuple()  # (10.0, 20.0, 30.0, 40.0)
```

---

## Circle

`Circle` represents a circle defined by a center point and a radius.

### Creating circles

```python
from engine import Circle, Vector2

c = Circle(Vector2(400, 300), 50)  # center=(400,300), radius=50
```

### Collision detection

#### `contains_point(point)` -- Is a point inside?

```python
c = Circle(Vector2(100, 100), 50)

c.contains_point(Vector2(100, 100))  # True  -- center
c.contains_point(Vector2(130, 100))  # True  -- inside
c.contains_point(Vector2(200, 200))  # False -- outside
```

#### `overlaps_circle(other)` -- Circle-circle overlap

Two circles overlap if the distance between their centers is less than the sum
of their radii.

```python
a = Circle(Vector2(0, 0), 50)
b = Circle(Vector2(80, 0), 50)
c = Circle(Vector2(200, 0), 50)

a.overlaps_circle(b)  # True  -- distance 80 < 50 + 50
a.overlaps_circle(c)  # False -- distance 200 > 50 + 50
```

```
    +---------+
   /     a     \     +---------+
  |  (0,0) r=50 |--| (80,0) r=50 |
   \           /     \         /
    +---------+       +-------+

  Overlap! Distance (80) < sum of radii (100)
```

#### `overlaps_rect(rect)` -- Circle-AABB overlap

Tests whether the circle overlaps an axis-aligned rectangle. The algorithm finds
the closest point on the rectangle to the circle's center and checks if it is
within the radius.

```python
c = Circle(Vector2(150, 150), 30)
r = Rect(100, 100, 100, 100)

c.overlaps_rect(r)  # True
```

#### `get_bounds()` -- Bounding AABB

Returns the smallest axis-aligned rectangle that contains the circle.

```python
c = Circle(Vector2(100, 100), 50)
bounds = c.get_bounds()  # Rect(50, 50, 100, 100)
```

---

## Transform2D

`Transform2D` bundles position, rotation, and scale into a single object. Every
`Entity` automatically has a `Transform2D` attached. Components can access it
via `self.transform` (shortcut for `self.entity.transform`).

### Creating transforms

```python
from engine import Transform2D, Vector2

# Default: position=(0,0), rotation=0, scale=(1,1)
t = Transform2D()

# Custom
t = Transform2D(
    position=Vector2(400, 300),
    rotation=45.0,               # degrees
    scale=Vector2(2.0, 2.0),
)
```

### Fields

| Field | Type | Description |
|---|---|---|
| `position` | `Vector2` | World position |
| `rotation` | `float` | Rotation in degrees |
| `scale` | `Vector2` | Scale factor per axis |

### The `forward` property

Returns a unit vector pointing in the direction of the transform's rotation.

```python
t = Transform2D(rotation=0)
t.forward  # Vector2(1, 0) -- pointing right

t.rotation = 90
t.forward  # Vector2(0, 1) -- pointing down (screen coords)

t.rotation = 180
t.forward  # Vector2(-1, 0) -- pointing left
```

This is useful for moving an entity in the direction it is facing:

```python
class BulletMovement(engine.Component):
    def on_start(self):
        self.speed = 500.0

    def on_update(self, dt):
        self.position = self.position + self.transform.forward * self.speed * dt
```

### Methods

#### `translate(offset)` -- Move by offset

```python
t = Transform2D(position=Vector2(100, 100))
t.translate(Vector2(10, -5))
# t.position is now Vector2(110, 95)
```

#### `look_at(target)` -- Face a target point

Sets the rotation so that `forward` points toward the target.

```python
t = Transform2D(position=Vector2(100, 100))
t.look_at(Vector2(200, 100))
# t.rotation is now 0.0 (pointing right toward the target)

t.look_at(Vector2(100, 200))
# t.rotation is now 90.0 (pointing down toward the target)
```

---

## Utility Functions

The `engine.math.utils` module provides common math utility functions. Import
them like this:

```python
from engine.math import utils

# or import specific functions
from engine.math.utils import lerp, clamp, remap, smoothstep
```

### `lerp(a, b, t)` -- Linear interpolation

Returns a value between `a` and `b` based on `t` (0 to 1).

```python
lerp(0, 100, 0.0)   # 0.0
lerp(0, 100, 0.5)   # 50.0
lerp(0, 100, 1.0)   # 100.0
lerp(0, 100, 0.25)  # 25.0
```

```
  a=0                                         b=100
  |-----------|-----------|-----------|---------|
  t=0        t=0.25      t=0.5      t=0.75    t=1.0
  result: 0   25          50         75        100
```

**Common use case -- smooth camera follow (in a CameraFollow component):**

```python
class CameraFollow(engine.Component):
    def on_late_update(self, dt):
        target = self.entity  # or a reference to the target entity
        camera_pos = camera_pos.lerp(target.position, 3.0 * dt)
```

By lerping each frame with `t = speed * dt`, the camera smoothly approaches the
target, moving fast when far away and slowing down as it gets close.

### `clamp(value, min_val, max_val)` -- Restrict to range

```python
clamp(150, 0, 100)   # 100  -- capped at max
clamp(-10, 0, 100)   # 0    -- capped at min
clamp(50, 0, 100)    # 50   -- within range, unchanged
```

**Common use case -- keep entity inside bounds:**

```python
class BoundsClamp(engine.Component):
    def on_late_update(self, dt):
        from engine.math.utils import clamp
        app = engine.current_app()
        self.position = engine.Vector2(
            clamp(self.position.x, 0, app.width),
            clamp(self.position.y, 0, app.height),
        )
```

### `remap(value, from_min, from_max, to_min, to_max)` -- Map between ranges

Converts a value from one range to another.

```python
# Map a health value (0-100) to a bar width (0-200 pixels)
bar_width = remap(health, 0, 100, 0, 200)

# Map mouse X (0-800) to a color value (0-255)
red = remap(mouse_x, 0, 800, 0, 255)
```

```
  from_min=0   value=50   from_max=100
  |------------|----------|
                    |
                    v  remap
  |------------|----------|
  to_min=0    result=100  to_max=200
```

### `inverse_lerp(a, b, value)` -- Inverse of lerp

Given a value between `a` and `b`, returns the corresponding `t`.

```python
inverse_lerp(0, 100, 0)    # 0.0
inverse_lerp(0, 100, 50)   # 0.5
inverse_lerp(0, 100, 100)  # 1.0
inverse_lerp(0, 100, 25)   # 0.25
```

This is the reverse of `lerp`: if `lerp(a, b, t)` gives you a value, then
`inverse_lerp(a, b, value)` gives you back `t`.

### `smoothstep(edge0, edge1, x)` -- Smooth Hermite interpolation

Returns a smooth S-curve value between 0 and 1. Unlike `lerp`, which is linear,
`smoothstep` starts slowly, accelerates in the middle, and decelerates at the
end.

```python
smoothstep(0, 1, 0.0)   # 0.0
smoothstep(0, 1, 0.25)  # 0.15625
smoothstep(0, 1, 0.5)   # 0.5
smoothstep(0, 1, 0.75)  # 0.84375
smoothstep(0, 1, 1.0)   # 1.0
```

```
  1.0 |                  ______
      |                /
      |              /
      |            /
      |          /      <-- smoothstep (S-curve)
      |        /
      |      /
      |   __/
  0.0 |__/
      +-----|------|------|----->
       edge0              edge1


  1.0 |                  /
      |                /
      |              /
      |            /    <-- lerp (linear, for comparison)
      |          /
      |        /
      |      /
      |    /
  0.0 |  /
      +-----|------|------|----->
       edge0              edge1
```

The `x` value is clamped to the `[edge0, edge1]` range, so values outside the
range return 0 or 1.

**Common use cases:**

- Smooth fade-in/fade-out animations
- Easing transitions between values
- UI element appear/disappear effects

```python
class FadeIn(engine.Component):
    def on_start(self):
        self.elapsed = 0.0

    def on_update(self, dt):
        self.elapsed += dt

    def on_draw(self, renderer):
        alpha = smoothstep(0, 2, self.elapsed)  # fade in over 2 seconds
        color = Color.WHITE.with_alpha(int(alpha * 255))
        p = self.position
        renderer.draw_rect(p.x - 25, p.y - 25, 50, 50, color)
```

---

## Practical Examples

### Normalize diagonal movement

Without normalization, moving diagonally (e.g., up+right) is about 41% faster
than moving in a single direction because the diagonal of a unit square is
sqrt(2).

```python
class Movement(engine.Component):
    def on_start(self):
        self.speed = 300.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        direction = Vector2.zero()
        if kb.is_pressed(Key.LEFT):
            direction = direction + Vector2.left()
        if kb.is_pressed(Key.RIGHT):
            direction = direction + Vector2.right()
        if kb.is_pressed(Key.UP):
            direction = direction + Vector2.up()
        if kb.is_pressed(Key.DOWN):
            direction = direction + Vector2.down()

        # Normalize so diagonal movement is the same speed
        if direction.magnitude > 0:
            self.transform.translate(direction.normalized * self.speed * dt)
```

### Distance-based aggro range

```python
class AggroAI(engine.Component):
    def on_start(self):
        self.aggro_range = 150.0

    def on_update(self, dt):
        world = self.entity._world
        players = world.find_by_tag("player")
        if players:
            player = players[0]
            distance = self.position.distance_to(player.position)
            if distance < self.aggro_range:
                self.chase(player)
            else:
                self.patrol()
```

### Smooth follow camera

```python
class CameraFollow(engine.Component):
    """Attach to a camera entity. Follows a target smoothly."""

    def on_start(self):
        self.target = None
        self.follow_speed = 3.0

    def on_late_update(self, dt):
        if self.target:
            self.position = self.position.lerp(
                self.target.position, self.follow_speed * dt
            )
```

### Screen-space collision

```python
player_rect = Rect(player.position.x - 16, player.position.y - 16, 32, 32)
coin_rect = Rect(coin.position.x - 8, coin.position.y - 8, 16, 16)

if player_rect.overlaps(coin_rect):
    collect_coin()
```

### Bullet facing direction

```python
class BulletMovement(engine.Component):
    def on_start(self):
        self.speed = 500.0

    def on_update(self, dt):
        # Move in the direction the bullet was aimed when spawned
        self.position = self.position + self.transform.forward * self.speed * dt

# Spawning a bullet from a shooting component:
class Shooter(engine.Component):
    def on_update(self, dt):
        mouse = engine.current_app().mouse
        if mouse.is_just_pressed(engine.MouseButton.LEFT):
            bullet = engine.Entity("bullet")
            bullet.position = self.position.copy()
            bullet.transform.look_at(mouse.position)
            bullet.add_component(BulletMovement())
            self.entity._world.add(bullet)
```

---

## Where to Go Next

| Topic | Document |
|---|---|
| Keyboard, mouse, input patterns | [Input](input.md) |
| Renderer, draw queue, colors, layers | [Rendering](rendering.md) |
| Entities, components, worlds | [ECS](ecs.md) |
| Scenes and scene management | [Scenes](scene.md) |
