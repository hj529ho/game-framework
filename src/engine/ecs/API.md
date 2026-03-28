# engine.ecs -- API Reference

## Class: `Component`

**File**: `component.py`
**Import**: `from engine.ecs.component import Component`
**Inherits**: `Lifecycle`

Base component class. Like Unity's `MonoBehaviour`.
Inherit and override lifecycle hooks to define behavior. Attach to an `Entity`.

### Constructor

```python
Component()
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `entity` | `Entity` | no | The entity this component is attached to. Raises `RuntimeError` if not attached. |
| `transform` | `Transform2D` | no | Shortcut for `self.entity.transform` |
| `position` | `Vector2` | yes | Shortcut for `self.entity.position` |
| `enabled` | `bool` | yes | If `False`, lifecycle hooks (`on_update`, `on_late_update`, `on_draw`, `on_fixed_update`) are skipped. Default: `True`. |

### Internal Fields (not part of public API)

| Field | Type | Description |
|---|---|---|
| `_entity` | `Entity \| None` | Set by `entity.add_component()` |
| `_started` | `bool` | Set to `True` after `on_start()` is called |
| `_enabled` | `bool` | Backing field for `enabled` property |

### Inherited Lifecycle Hooks

All hooks from `Lifecycle` are available. Override in subclass:

| Hook | Signature | When Called |
|---|---|---|
| `on_awake` | `() -> None` | When `entity.add_component()` is called |
| `on_start` | `() -> None` | Once, before first `on_update` |
| `on_fixed_update` | `(fixed_dt: float) -> None` | 0~N times per frame at fixed interval (default 1/50s) |
| `on_update` | `(dt: float) -> None` | Once per frame |
| `on_late_update` | `(dt: float) -> None` | After all `on_update` calls |
| `on_draw` | `(renderer: Renderer) -> None` | Render phase |
| `on_destroy` | `() -> None` | When removed or entity destroyed |

### Usage

```python
class PlayerMovement(Component):
    def on_start(self):
        self.speed = 200.0

    def on_update(self, dt):
        kb = current_app().keyboard
        if kb.is_pressed(Key.RIGHT):
            self.transform.translate(Vector2.right() * self.speed * dt)

player = Entity("Player")
player.add_component(PlayerMovement())
scene.add(player)
```

---

## Class: `Entity`

**File**: `entity.py`
**Import**: `from engine.ecs.entity import Entity`

Game object container. Like Unity's `GameObject`.
Entity itself has NO behavior -- all logic goes in Components.
Entity provides a `Transform2D` and manages its attached Components.

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
| `position` | `Vector2` | yes | Shortcut for `transform.position` |
| `rotation` | `float` | yes | Shortcut for `transform.rotation` (degrees) |
| `scale` | `Vector2` | yes | Shortcut for `transform.scale` |
| `active` | `bool` | yes | If `False`, all component hooks are skipped |
| `tags` | `set[str]` | no | Read-only view of the tag set |
| `parent` | `Entity \| None` | no | Parent entity in hierarchy |
| `children` | `list[Entity]` | no | Copy of children list |
| `components` | `list[Component]` | no | Copy of components list |

### Component Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add_component` | `(component: T) -> T` | `T` | Attach a component instance. Calls `on_awake()`. Raises `ValueError` if component is already attached to another entity. |
| `get_component` | `(comp_type: type[T]) -> T \| None` | `T \| None` | Get first component matching the type |
| `get_components` | `(comp_type: type[T]) -> list[T]` | `list[T]` | Get all components matching the type |
| `has_component` | `(comp_type: type[Component]) -> bool` | `bool` | Check if at least one of the type is attached |
| `remove_component` | `(component: Component) -> None` | `None` | Remove a specific component instance. Calls `on_destroy()`. |
| `remove_components` | `(comp_type: type[Component]) -> None` | `None` | Remove all components of a given type |

### Tag Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add_tag` | `(tag: str)` | `None` | Add a tag |
| `has_tag` | `(tag: str)` | `bool` | Check if tag is present |

### Hierarchy Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add_child` | `(child: Entity)` | `None` | Add child. Removes from previous parent if any. Auto-adds to same World if parent is in one. |
| `remove_child` | `(child: Entity)` | `None` | Remove child relationship |

### Usage

```python
player = Entity("Player")
player.position = Vector2(400, 300)
player.add_component(PlayerMovement())
player.add_component(SpriteRenderer("player.png"))
player.add_tag("player")
scene.add(player)

# Query
sprite = player.get_component(SpriteRenderer)
has_collider = player.has_component(BoxCollider)
```

---

## Class: `World`

**File**: `world.py`
**Import**: `from engine.ecs.world import World`

Entity container with deferred add/remove and lifecycle hook dispatch.

### Constructor

```python
World(fixed_timestep: float = 1.0 / 50.0)  # default: 20ms (50Hz)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `entities` | `list[Entity]` | no | Copy of current entity list |
| `fixed_timestep` | `float` | yes | Fixed update interval in seconds. Default: `1/50`. |
| `len(world)` | `int` | no | Number of entities via `__len__` |

### Mutation Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add` | `(entity: Entity)` | `Entity` | Queue entity for addition. Processed on next `update()`. |
| `remove` | `(entity: Entity)` | `None` | Queue entity for removal. Processed on next `update()`. |
| `clear` | `()` | `None` | Immediately destroy and remove ALL entities (calls `on_destroy`). |

### Frame Methods

| Method | Signature | Description |
|---|---|---|
| `update` | `(dt: float) -> None` | Full update cycle (see below). |
| `draw` | `(renderer: Renderer) -> None` | Call `on_draw(renderer)` on all active entity components. |

### Query Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `find_by_name` | `(name: str)` | `Entity \| None` | First entity with matching name |
| `find_by_tag` | `(tag: str)` | `list[Entity]` | All entities with the given tag |
| `find_by_type` | `(entity_type: type[T])` | `list[T]` | All entities that are instances of the given type |
| `find_with_component` | `(*comp_types: type[Component])` | `list[Entity]` | All entities that have ALL given component types |

### Update Cycle Detail

```
world.update(dt):
  1. _process_additions()                 -- add queued entities to list, set entity._world
  2. entity._start_components()           -- on_start for components not yet started
  3. _fixed_accumulator += dt             -- fixed update accumulator
     while _fixed_accumulator >= fixed_timestep:
       entity._fixed_update_components(fixed_timestep)  -- 0~N times
       _fixed_accumulator -= fixed_timestep
  4. entity._update_components(dt)        -- on_update (once per frame)
  5. entity._late_update_components(dt)   -- on_late_update (once per frame)
  6. _process_removals()                  -- on_destroy + remove queued entities
```

Steps 2-5 only run on entities where `entity.active == True`.
