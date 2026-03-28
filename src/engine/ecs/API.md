# engine.ecs -- API Reference

## Class: `Component`

**File**: `component.py`
**Import**: `from engine.ecs import Component`
**Inherits**: `Lifecycle`

Base component class. Like Unity's MonoBehaviour.
Inherit and override lifecycle hooks to define behavior. Attach to Entity.

### Constructor

```python
Component()
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `entity` | `Entity` | no | The entity this component is attached to. Raises RuntimeError if not attached. |
| `transform` | `Transform2D` | no | Shortcut for `self.entity.transform` |
| `position` | `Vector2` | yes | Shortcut for `self.entity.position` |
| `enabled` | `bool` | yes | If False, lifecycle hooks are skipped (except on_destroy) |

### Inherited Lifecycle Hooks

| Hook | Signature | When Called |
|---|---|---|
| `on_awake` | `()` | When `entity.add_component()` is called |
| `on_start` | `()` | Once, before first `on_update` |
| `on_fixed_update` | `(fixed_dt: float)` | 0~N times per frame at fixed interval (default 1/50s) |
| `on_update` | `(dt: float)` | Once per frame |
| `on_late_update` | `(dt: float)` | After all `on_update` calls |
| `on_draw` | `(renderer: Renderer)` | Render phase |
| `on_destroy` | `()` | When removed or entity destroyed |

### Usage

```python
class PlayerMovement(Component):
    def on_start(self):
        self.speed = 200.0

    def on_update(self, dt):
        kb = current_app().keyboard
        if kb.is_pressed(Key.RIGHT):
            self.transform.translate(Vector2.right() * self.speed * dt)

class SpriteRenderer(Component):
    def on_awake(self):
        self.color = Color.BLUE
        self.size = 32

    def on_draw(self, renderer):
        p = self.position
        half = self.size / 2
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size, self.color)
```

---

## Class: `Entity`

**File**: `entity.py`
**Import**: `from engine.ecs import Entity`

Game object container. Like Unity's GameObject.
Entity itself has NO behavior -- all logic goes in Components.

### Constructor

```python
Entity(name: str = "")  # auto-generates "Entity_{id}" if empty
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `id` | `int` | no | Auto-incremented unique ID |
| `name` | `str` | yes | Display name |
| `transform` | `Transform2D` | no | Full transform object |
| `position` | `Vector2` | yes | Shortcut for transform.position |
| `rotation` | `float` | yes | Shortcut for transform.rotation (degrees) |
| `scale` | `Vector2` | yes | Shortcut for transform.scale |
| `active` | `bool` | yes | If False, all component hooks are skipped |
| `tags` | `set[str]` | no | Read-only tag set |
| `parent` | `Entity \| None` | no | Parent entity |
| `children` | `list[Entity]` | no | Copy of children list |
| `components` | `list[Component]` | no | Copy of components list |

### Component Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add_component` | `(component: T) -> T` | `T` | Attach component instance. Calls `on_awake()`. |
| `get_component` | `(comp_type: type[T]) -> T \| None` | `T \| None` | Get first component of type |
| `get_components` | `(comp_type: type[T]) -> list[T]` | `list[T]` | Get all components of type |
| `has_component` | `(comp_type: type[Component]) -> bool` | `bool` | Check if type is attached |
| `remove_component` | `(component: Component) -> None` | `None` | Remove specific instance. Calls `on_destroy()`. |
| `remove_components` | `(comp_type: type[Component]) -> None` | `None` | Remove all of a type |

### Tag Methods

| Method | Signature | Description |
|---|---|---|
| `add_tag` | `(tag: str)` | Add tag |
| `has_tag` | `(tag: str) -> bool` | Check tag |

### Hierarchy Methods

| Method | Signature | Description |
|---|---|---|
| `add_child` | `(child: Entity)` | Add child, auto-add to same World |
| `remove_child` | `(child: Entity)` | Remove child |

### Usage

```python
player = Entity("Player")
player.position = Vector2(400, 300)
player.add_component(PlayerMovement())
player.add_component(SpriteRenderer())
player.add_tag("player")
scene.add(player)
```

---

## Class: `World`

**File**: `world.py`
**Import**: `from engine.ecs import World`

Entity container. Manages lifecycle hook dispatch with deferred add/remove.

### Constructor

```python
World(fixed_timestep: float = 1.0 / 50.0)  # default: 20ms (50Hz)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `entities` | `list[Entity]` | no | Copy of current entities |
| `len(world)` | `int` | no | Number of entities |
| `fixed_timestep` | `float` | yes | Fixed update interval in seconds (default 1/50) |

### Methods

| Method | Signature | Description |
|---|---|---|
| `add` | `(entity: Entity) -> Entity` | Queue for addition |
| `remove` | `(entity: Entity) -> None` | Queue for removal |
| `update` | `(dt: float) -> None` | Full cycle: add -> start -> fixed_update(0~N) -> update -> late_update -> remove |
| `draw` | `(renderer: Renderer) -> None` | Call on_draw on all active components |
| `clear` | `() -> None` | Immediately remove all (calls on_destroy) |

### Query Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `find_by_name` | `(name: str)` | `Entity \| None` | First match by name |
| `find_by_tag` | `(tag: str)` | `list[Entity]` | All with tag |
| `find_by_type` | `(type)` | `list[Entity]` | All of entity subclass type |
| `find_with_component` | `(*comp_types)` | `list[Entity]` | All with ALL given component types |

### Update Cycle Detail

```
world.update(dt):
  1. _process_additions()                 -- add queued entities to list
  2. entity._start_components()           -- on_start for components not yet started
  3. accumulator += dt                    -- fixed update accumulator
     while accumulator >= fixed_timestep:
       entity._fixed_update_components(fixed_dt)  -- on_fixed_update (0~N times)
       accumulator -= fixed_timestep
  4. entity._update_components(dt)        -- on_update (once per frame)
  5. entity._late_update_components(dt)   -- on_late_update (once per frame)
  6. _process_removals()                  -- on_destroy + remove queued entities
```
