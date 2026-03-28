# Entity-Component System (ECS)

The `engine.ecs` module provides a Unity-like component system. `Entity` is a
pure container (like Unity's `GameObject`) that holds a `Transform2D`, a list of
`Component` instances, tags, and child entities. All game logic lives in
`Component` subclasses, which define behavior through lifecycle hooks. A `World`
container manages entities with deferred add/remove to prevent mutation during
iteration.

---

## Component

`Component` is the base class for all game behavior. It inherits from
`Lifecycle`, which defines the hook methods. Like Unity's `MonoBehaviour`, you
subclass `Component`, override the hooks you need, and attach instances to
entities.

### Lifecycle hooks

| Hook | Signature | When Called | Typical Use |
|---|---|---|---|
| `on_awake` | `()` | Immediately when `entity.add_component()` is called | Initialize fields, set defaults |
| `on_start` | `()` | Once, before first `on_update`. All siblings are awake. | Init that depends on other components |
| `on_update` | `(dt: float)` | Every frame | Game logic, input, movement, AI |
| `on_late_update` | `(dt: float)` | Every frame, after ALL `on_update` calls | Camera follow, constraints |
| `on_draw` | `(renderer: Renderer)` | Every frame during render phase | Draw sprites, shapes, effects |
| `on_destroy` | `()` | When component is removed or entity is destroyed | Cleanup, release resources |

All hooks are no-ops by default. Override only the ones you need.

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `entity` | `Entity` | no | The entity this component is attached to. Raises `RuntimeError` if not attached. |
| `transform` | `Transform2D` | no | Shortcut for `self.entity.transform` |
| `position` | `Vector2` | yes | Shortcut for `self.entity.position` |
| `enabled` | `bool` | yes | If `False`, lifecycle hooks are skipped (except `on_destroy`) |

### Accessing engine systems

Use `current_app()` to access input, clock, and renderer from inside a
Component:

```python
class PlayerMovement(engine.Component):
    def on_update(self, dt):
        kb = engine.current_app().keyboard
        if kb.is_pressed(engine.Key.RIGHT):
            self.transform.translate(engine.Vector2.right() * 200 * dt)
```

### Defining a component

```python
import engine


class Movement(engine.Component):
    """Handles keyboard movement."""

    def on_start(self):
        self.speed = 300.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        dx, dy = 0.0, 0.0
        if kb.is_pressed(engine.Key.LEFT):  dx -= 1
        if kb.is_pressed(engine.Key.RIGHT): dx += 1
        if kb.is_pressed(engine.Key.UP):    dy -= 1
        if kb.is_pressed(engine.Key.DOWN):  dy += 1
        self.transform.translate(engine.Vector2(dx, dy) * self.speed * dt)


class BoxRenderer(engine.Component):
    """Draws a colored rectangle at the entity's position."""

    def on_awake(self):
        self.color = engine.Color.BLUE
        self.size = 32

    def on_draw(self, renderer):
        p = self.position
        half = self.size / 2
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size, self.color)
```

### The `enabled` flag

Setting `enabled = False` causes the engine to skip all lifecycle hooks for that
component (except `on_destroy`). This is useful for temporarily disabling
behavior:

```python
class Damageable(engine.Component):
    def on_start(self):
        self.hp = 100
        self.invincible_timer = 0.0

    def on_update(self, dt):
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                # Re-enable the damage-flash renderer
                flash = self.entity.get_component(DamageFlash)
                if flash:
                    flash.enabled = False

    def take_damage(self, amount):
        if self.invincible_timer <= 0:
            self.hp -= amount
            self.invincible_timer = 1.0
            flash = self.entity.get_component(DamageFlash)
            if flash:
                flash.enabled = True
```

### Data-only components

Not every component needs lifecycle hooks. Some are pure data containers that
other components read:

```python
class Health(engine.Component):
    def __init__(self, max_hp: int = 100):
        super().__init__()
        self.hp = max_hp
        self.max_hp = max_hp

    def damage(self, amount: int):
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)

    def is_dead(self) -> bool:
        return self.hp <= 0

    @property
    def health_pct(self) -> float:
        return self.hp / self.max_hp
```

---

## Entity

`Entity` is a pure game object container, like Unity's `GameObject`. It holds a
`Transform2D`, manages attached `Component` instances, provides tags for
categorization, and supports parent/child hierarchy. Entity itself has **no**
lifecycle hooks and **no** behavior -- all logic goes in Components.

### Creating entities

```python
from engine import Entity, Vector2

# Direct instantiation
rock = Entity("rock")
rock.position = Vector2(200, 150)

# Add components to give it behavior
rock.add_component(BoxRenderer())
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `id` | `int` | no | Auto-incremented unique ID |
| `name` | `str` | yes | Display name |
| `transform` | `Transform2D` | no | Full transform object |
| `position` | `Vector2` | yes | Shortcut for `transform.position` |
| `rotation` | `float` | yes | Shortcut for `transform.rotation` (degrees) |
| `scale` | `Vector2` | yes | Shortcut for `transform.scale` |
| `active` | `bool` | yes | If `False`, all component hooks are skipped |
| `tags` | `set[str]` | no | Read-only tag set |
| `parent` | `Entity \| None` | no | Parent entity |
| `children` | `list[Entity]` | no | Copy of children list |
| `components` | `list[Component]` | no | Copy of components list |

### Transform shortcuts

Every entity has a `Transform2D`, and the most common fields are exposed as
direct properties for convenience:

```python
entity.position            # same as entity.transform.position
entity.position = pos      # same as entity.transform.position = pos

entity.rotation            # same as entity.transform.rotation
entity.rotation = 45.0     # same as entity.transform.rotation = 45.0

entity.scale               # same as entity.transform.scale
entity.scale = Vector2(2, 2)

# Full transform access when you need it
entity.transform.translate(Vector2(10, 0))
entity.transform.look_at(target_pos)
entity.transform.forward   # unit vector in rotation direction
```

### Component management

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add_component` | `(component: T) -> T` | `T` | Attach component instance. Calls `on_awake()`. |
| `get_component` | `(comp_type: type[T]) -> T \| None` | `T \| None` | Get first component of type |
| `get_components` | `(comp_type: type[T]) -> list[T]` | `list[T]` | Get all components of type |
| `has_component` | `(comp_type: type[Component]) -> bool` | `bool` | Check if type is attached |
| `remove_component` | `(component: Component) -> None` | `None` | Remove specific instance. Calls `on_destroy()`. |
| `remove_components` | `(comp_type: type[Component]) -> None` | `None` | Remove all of a type |

```python
# Add components to an entity
player = Entity("Player")
player.add_component(Movement())
health = player.add_component(Health(100))

# Get a component by type
hp = player.get_component(Health)
hp.damage(25)
print(hp.hp)  # 75

# Check if a component exists
player.has_component(Health)  # True

# Remove a specific component instance
player.remove_component(health)
player.has_component(Health)  # False
```

### Tags

Tags are lightweight string labels for categorizing entities:

```python
enemy = Entity("goblin")
enemy.add_tag("enemy")
enemy.add_tag("ground_unit")

enemy.has_tag("enemy")       # True
enemy.has_tag("flying_unit") # False

# Query from a World
all_enemies = world.find_by_tag("enemy")
```

### Parent/child hierarchy

Entities can be organized in a tree structure:

```python
ship = Entity("ship")
turret = Entity("turret")

ship.add_child(turret)      # turret is now a child of ship
print(turret.parent)        # <Entity 'ship' ...>
print(ship.children)        # [<Entity 'turret' ...>]

ship.remove_child(turret)   # turret is detached
```

When you call `add_child`:

1. If the child already has a parent, it is removed from the old parent.
2. The child's `parent` property is set.
3. If the parent is in a World and the child is not, the child is automatically
   added to the same World.

### The `active` flag

Setting `active = False` causes the engine to skip all component hooks for that
entity. The entity remains in the world but is effectively paused and invisible.

---

## World

`World` is a container that holds entities and dispatches lifecycle hooks to
their components. It handles deferred add/remove to prevent bugs from modifying
the entity list during iteration.

### Basic usage

```python
from engine import World

world = World()

# Add entities (deferred -- actual add happens in next update())
player = world.add(Entity("player"))
enemy = world.add(Entity("enemy"))

# Called by the engine each frame:
world.update(dt)           # process adds, start, update, late_update, remove
world.draw(renderer)       # call on_draw on all active components
```

### Deferred add/remove

Entities are **not** added or removed immediately when you call `world.add()` or
`world.remove()`. They are placed in a queue and processed during `world.update()`:

```
world.update(dt):

  Step 1: _process_additions()
     For each entity in _to_add:
       - Set entity._world = self
       - Append to _entities list
     Clear _to_add

  Step 2: _start_components()
     For each active entity:
       - Call on_start() on components that haven't started yet

  Step 3: _update_components(dt)
     For each active entity:
       - Call on_update(dt) on all enabled components

  Step 4: _late_update_components(dt)
     For each active entity:
       - Call on_late_update(dt) on all enabled components

  Step 5: _process_removals()
     For each entity in _to_remove:
       - Call on_destroy() on all components
       - Set entity._world = None
       - Remove from _entities list
     Clear _to_remove
```

This prevents a common class of bugs:

```python
class SelfDestruct(engine.Component):
    def on_update(self, dt):
        if self.entity.get_component(Health).is_dead():
            self.entity._world.remove(self.entity)  # queued, not immediate
            # The entity continues to exist until the end of update()
```

### Timeline of deferred operations

```
Frame N                        Frame N+1
  |                               |
  |  world.add(entity_A)          |
  |  world.add(entity_B)          |
  |                               |
  |  world.update(dt):            |  world.update(dt):
  |    [process additions]        |    ...
  |      A added to list          |
  |      B added to list          |
  |    [start new components]     |
  |      A components: on_start() |
  |      B components: on_start() |
  |    [update all]               |
  |      A: on_update(dt)         |
  |      B: on_update(dt)         |
  |      B calls world.remove(B)  |
  |    [late update all]          |
  |      A: on_late_update(dt)    |
  |      B: on_late_update(dt)    |
  |    [process removals]         |
  |      B: on_destroy()          |
  |                               |
  |  world.draw(renderer):        |
  |    A: on_draw(renderer)       |
  |    -- B is already removed -- |
```

### Query methods

The World provides several ways to find entities:

```python
# By name (returns first match or None)
player = world.find_by_name("player")

# By tag (returns a list)
enemies = world.find_by_tag("enemy")

# By type (returns all instances of that entity type)
all_bullets = world.find_by_type(BulletEntity)

# By component types (entities that have ALL specified components)
damageable = world.find_with_component(Health)
moving_damageable = world.find_with_component(Health, Movement)
```

### Other methods

```python
len(world)          # number of entities currently in the world
world.entities      # copy of the entity list (safe to iterate)
world.clear()       # immediately remove all entities, calling on_destroy() on each
```

---

## Component Composition Patterns

The engine's component system encourages composition over inheritance. Here is
guidance on how to structure your game objects.

### Separate concerns into different components

Each component should handle one responsibility. Combine them on entities to
build complex behavior:

```python
# Movement component -- handles input and movement
class Movement(engine.Component):
    def on_start(self):
        self.speed = 300.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        d = engine.Vector2.zero()
        if kb.is_pressed(engine.Key.LEFT):  d = d + engine.Vector2.left()
        if kb.is_pressed(engine.Key.RIGHT): d = d + engine.Vector2.right()
        if d.magnitude > 0:
            self.transform.translate(d.normalized * self.speed * dt)


# Health component -- tracks HP
class Health(engine.Component):
    def __init__(self, max_hp=100):
        super().__init__()
        self.hp = max_hp
        self.max_hp = max_hp

    def damage(self, amount):
        self.hp = max(0, self.hp - amount)


# Renderer component -- draws the entity
class BoxRenderer(engine.Component):
    def on_awake(self):
        self.color = engine.Color.BLUE
        self.size = 40

    def on_draw(self, renderer):
        p = self.position
        half = self.size / 2
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size, self.color)


# Compose them together
player = engine.Entity("Player")
player.position = engine.Vector2(400, 300)
player.add_component(Movement())
player.add_component(Health(100))
player.add_component(BoxRenderer())
```

### Reuse components across entity types

The same component class can be attached to different entities:

```python
# Player has movement, health, and a renderer
player = engine.Entity("Player")
player.add_component(Movement())
player.add_component(Health(100))
box = player.add_component(BoxRenderer())
box.color = engine.Color.BLUE

# Enemy also has health and a renderer, but different movement
enemy = engine.Entity("Goblin")
enemy.add_component(PatrolAI())        # different movement behavior
enemy.add_component(Health(50))
box = enemy.add_component(BoxRenderer())
box.color = engine.Color.RED

# Barrel only has health and a renderer (no movement)
barrel = engine.Entity("Barrel")
barrel.add_component(Health(20))
box = barrel.add_component(BoxRenderer())
box.color = engine.Color.ORANGE
```

### Components that reference sibling components

Use `on_start` to get references to other components on the same entity:

```python
class HealthBar(engine.Component):
    """Draws a health bar above the entity. Requires a Health component."""

    def on_start(self):
        self.health = self.entity.get_component(Health)

    def on_draw(self, renderer):
        if self.health is None:
            return
        p = self.position
        bar_width = 40
        bar_height = 4
        y_offset = -25

        # Background (red)
        renderer.draw_rect(
            p.x - bar_width / 2, p.y + y_offset,
            bar_width, bar_height,
            engine.Color.RED, layer=1,
        )
        # Foreground (green, scaled by health %)
        renderer.draw_rect(
            p.x - bar_width / 2, p.y + y_offset,
            bar_width * self.health.health_pct, bar_height,
            engine.Color.GREEN, layer=1,
        )
```

---

## Practical Examples

### Example 1: Player with keyboard movement

```python
class PlayerMovement(engine.Component):
    def on_start(self):
        self.speed = 300.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        direction = engine.Vector2.zero()

        if kb.is_pressed(engine.Key.LEFT):  direction = direction + engine.Vector2.left()
        if kb.is_pressed(engine.Key.RIGHT): direction = direction + engine.Vector2.right()
        if kb.is_pressed(engine.Key.UP):    direction = direction + engine.Vector2.up()
        if kb.is_pressed(engine.Key.DOWN):  direction = direction + engine.Vector2.down()

        if direction.magnitude > 0:
            self.transform.translate(direction.normalized * self.speed * dt)


class PlayerRenderer(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(p.x - 20, p.y - 20, 40, 40, engine.Color.BLUE)
```

### Example 2: Enemy that patrols back and forth

```python
import math

class PatrolMovement(engine.Component):
    def on_start(self):
        self.timer = 0.0
        self.start_pos = self.position.copy()
        self.patrol_range = 100.0
        self.patrol_speed = 2.0

    def on_update(self, dt):
        self.timer += dt
        offset_x = math.sin(self.timer * self.patrol_speed) * self.patrol_range
        self.position = self.start_pos + engine.Vector2(offset_x, 0)


class EnemyRenderer(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(p.x - 15, p.y - 15, 30, 30, engine.Color.RED)
```

### Example 3: Projectile with lifetime

```python
class BulletMovement(engine.Component):
    def on_start(self):
        self.speed = 500.0
        self.lifetime = 3.0  # seconds

    def on_update(self, dt):
        # Move forward
        self.position = self.position + self.transform.forward * self.speed * dt

        # Destroy after lifetime expires
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.entity._world.remove(self.entity)


class BulletRenderer(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(p.x - 4, p.y - 4, 8, 8, engine.Color.YELLOW)
```

**Spawning a bullet from a shooter component:**

```python
class Shooter(engine.Component):
    def on_start(self):
        self.shoot_cooldown = 0.0

    def on_update(self, dt):
        self.shoot_cooldown -= dt
        mouse = engine.current_app().mouse

        if mouse.is_just_pressed(engine.MouseButton.LEFT) and self.shoot_cooldown <= 0:
            bullet = engine.Entity("bullet")
            bullet.position = self.position.copy()
            bullet.transform.look_at(mouse.position)
            bullet.add_component(BulletMovement())
            bullet.add_component(BulletRenderer())
            self.entity._world.add(bullet)
            self.shoot_cooldown = 0.2
```

### Example 4: Camera follow with on_late_update

```python
class CameraFollow(engine.Component):
    """Follows a target entity smoothly. Uses on_late_update so that the
    target's position is already updated for this frame."""

    def on_start(self):
        self.target_name = "Player"
        self.follow_speed = 5.0

    def on_late_update(self, dt):
        target = self.entity._world.find_by_name(self.target_name)
        if target:
            self.position = self.position.lerp(
                target.position, self.follow_speed * dt
            )
```

### Example 5: Querying entities by component

```python
class DamageAllEnemies(engine.Component):
    """Damages all entities that have Health and are tagged as 'enemy'."""

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        if kb.is_just_pressed(engine.Key.X):
            world = self.entity._world
            for entity in world.find_with_component(Health):
                if entity.has_tag("enemy"):
                    entity.get_component(Health).damage(10)
```

---

## Component Lifecycle Summary

```
                  entity.add_component(comp)
                       |
                       v
                  comp.on_awake()         <-- initialize fields here
                       |
                       v
                  scene.add(entity) / world.add(entity)
                       |
                       v
               (queued in _to_add)
                       |
                       v
              world.update(dt) starts
                       |
                       v
               comp.on_start()            <-- init depending on siblings
                       |
                       v
         +---> comp.on_update(dt)         <-- runs every frame (if enabled)
         |             |
         |             v
         |     comp.on_late_update(dt)    <-- runs every frame (if enabled)
         |             |
         +-------------+
                       |
                  (render phase)
                       |
                       v
               comp.on_draw(renderer)     <-- runs every frame (if enabled)
                       |
                  world.remove(entity)
                       |
                       v
               (queued in _to_remove)
                       |
                       v
              world.update(dt) ends
                       |
                       v
               comp.on_destroy()          <-- clean up here
```

---

## Where to Go Next

| Topic | Document |
|---|---|
| Scenes and scene management | [Scenes](scene.md) |
| Renderer, draw queue, colors, layers | [Rendering](rendering.md) |
| Keyboard, mouse, input patterns | [Input](input.md) |
