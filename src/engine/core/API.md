# engine.core -- API Reference

## Class: `Lifecycle`

**File**: `lifecycle.py`
**Import**: `from engine.core.lifecycle import Lifecycle`

Base class defining game object lifecycle hooks. `Component` inherits from this.
The engine calls these hooks automatically in a defined order each frame.

### Lifecycle Hook Order

```
First frame only:
  on_awake()              -- when component is added to entity
  on_start()              -- before first on_update (all components on entity are awake)

Every frame (fixed timestep, 0~N times):
  on_fixed_update(fixed_dt)  -- physics, deterministic simulation

Every frame (once):
  on_update(dt)           -- game logic, input
  on_late_update(dt)      -- post-update (camera, constraints)

Render phase:
  on_draw(renderer)       -- visual output

Cleanup:
  on_destroy()            -- when component or entity is removed
```

### Methods (all no-op by default, override in subclass)

| Method | Signature | When Called |
|---|---|---|
| `on_awake` | `() -> None` | Immediately when `entity.add_component()` is called |
| `on_start` | `() -> None` | Once, before first `on_update`. All sibling components are awake. |
| `on_fixed_update` | `(fixed_dt: float) -> None` | 0~N times per frame at fixed interval (default 1/50s = 20ms). `fixed_dt` is always `fixed_timestep`. |
| `on_update` | `(dt: float) -> None` | Once per frame. `dt` = seconds since last frame (variable). |
| `on_late_update` | `(dt: float) -> None` | Once per frame, after ALL `on_update` calls across all entities. |
| `on_draw` | `(renderer: Renderer) -> None` | Every frame during render phase. |
| `on_destroy` | `() -> None` | When component is removed or entity is destroyed. |

### fixed_update vs update

- `on_fixed_update(fixed_dt)`: Called at a fixed interval (default 1/50s = 20ms). Use for physics, collision response, and deterministic simulation. If the frame rate drops, multiple calls occur per frame to catch up. `fixed_dt` is always the same value.
- `on_update(dt)`: Called once per frame. `dt` is variable (depends on frame time). Use for input handling and general game logic.

---

## Class: `Game`

**File**: `game.py`
**Import**: `from engine.core.game import Game`

Main entry point. Creates `App` (SDL2 window) and runs the game loop internally.
Developers do NOT write a while loop -- `Game.run()` handles everything.

### Constructor

```python
Game(
    title: str = "Game",
    width: int = 800,
    height: int = 600,
    fps: int = 60,
    vsync: bool = True,
    resizable: bool = False,
    clear_color: Color | None = None,
)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `app` | `App` | no | The underlying SDL2 app (window, renderer, input, clock) |
| `scenes` | `SceneManager` | no | Scene stack manager |
| `width` | `int` | no | Window width |
| `height` | `int` | no | Window height |

### Methods

| Method | Signature | Description |
|---|---|---|
| `run` | `(initial_scene: Scene) -> None` | Start the game loop. Blocks until `quit()` or window close. |
| `quit` | `() -> None` | Stop the game loop (sets `app.running = False`). |

### Lifecycle Per Frame (inside `run`)

```
1. App.poll_events()                       -- SDL event polling, input state update
2. Clock.tick()                            -- delta time calculation
3. SceneManager.update(dt):
   a. Transition update (if active)
   b. Scene.update(dt) -> World.update(dt):
      i.   Process pending entity additions
      ii.  Component.on_start() for new components
      iii. Component.on_fixed_update(fixed_dt) -- 0~N times (accumulator)
      iv.  Component.on_update(dt)
      v.   Component.on_late_update(dt)
      vi.  Process pending entity removals
   c. SceneManager.process_pending() (scene transitions)
4. Renderer.begin_frame()                  -- clear screen
5. SceneManager.draw(renderer):
   a. Scene.draw(renderer) -> Component.on_draw(renderer)
   b. Transition.draw(renderer) (if active)
6. Renderer.end_frame()                    -- sort by layer, execute, present
```

### Usage

```python
game = Game(title="My Game", width=800, height=600)
game.run(MyScene())  # blocks here until game ends
```

---

## Class: `App`

**File**: `app.py`
**Import**: `from engine.core.app import App`

Low-level SDL2 wrapper. Created internally by `Game`. Access via `game.app` or `current_app()`.

### Constructor

```python
App(
    title: str = "Game",
    width: int = 800,
    height: int = 600,
    fps: int = 60,
    vsync: bool = True,
    resizable: bool = False,
    clear_color: Color | None = None,
)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `width` | `int` | no | Window width |
| `height` | `int` | no | Window height |
| `running` | `bool` | no | False after `quit()` or window close |
| `clock` | `Clock` | no | Frame timing |
| `keyboard` | `Keyboard` | no | Keyboard state |
| `mouse` | `Mouse` | no | Mouse state |
| `renderer` | `Renderer` | no | Draw command interface |
| `resources` | `ResourceManager` | no | Asset loading and caching |

### Methods

| Method | Signature | Description |
|---|---|---|
| `poll_events` | `() -> None` | Poll SDL events, update input state. Call once per frame before update. |
| `quit` | `() -> None` | Set `running = False` |
| `destroy` | `() -> None` | Cleanup all SDL resources (renderer, window, subsystems) |

---

## Function: `current_app`

**File**: `app.py`
**Import**: `from engine.core.app import current_app`

```python
current_app() -> App
```

Returns the active `App` instance. Raises `RuntimeError` if no App is running.
Use inside Components to access input, clock, resources, etc.

```python
class MyComponent(Component):
    def on_update(self, dt):
        kb = current_app().keyboard
        if kb.is_pressed(Key.SPACE):
            pass  # handle input
```

---

## Class: `Clock`

**File**: `clock.py`
**Import**: `from engine.core.clock import Clock`

High-resolution frame timing via SDL2 performance counters.

### Constructor

```python
Clock(target_fps: int = 60)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `dt` | `float` | no | Last frame delta time in seconds |
| `fps` | `float` | no | Smoothed FPS (updated every 0.5 seconds) |
| `total_time` | `float` | no | Total elapsed time in seconds |
| `frame_count` | `int` | no | Total frames ticked |
| `target_fps` | `int` | yes | FPS cap target. Setting changes frame limiting. |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `tick` | `() -> float` | `float` | Advance clock, return delta time in seconds. Applies frame limiting via `SDL_Delay`. |

---

## Class: `Event`

**File**: `events.py`
**Import**: `from engine.core.events import Event`

Base event class. Frozen dataclass. Subclass to define custom events.

```python
@dataclass(frozen=True)
class Event:
    pass
```

### Built-in Event Subclasses

| Class | Fields | Description |
|---|---|---|
| `SceneChangedEvent` | `old_scene: str, new_scene: str` | Scene transition occurred |
| `EntityCreatedEvent` | `entity_name: str` | Entity added to world |
| `EntityDestroyedEvent` | `entity_name: str` | Entity removed from world |
| `CollisionEvent` | `entity_a: str, entity_b: str` | Two entities collided |

### Custom Event Example

```python
@dataclass(frozen=True)
class PlayerDiedEvent(Event):
    player_name: str
    killer_name: str
```

---

## Class: `EventBus`

**File**: `events.py`
**Import**: `from engine.core.events import EventBus`

Decoupled publish/subscribe event system.

### Constructor

```python
EventBus()
```

### Methods

| Method | Signature | Description |
|---|---|---|
| `on` | `(event_type: type[Event], callback: Callable[[Event], None], priority: int = 0) -> None` | Subscribe. Lower priority runs first. |
| `off` | `(event_type: type[Event], callback: Callable) -> None` | Unsubscribe a specific callback. |
| `emit` | `(event: Event) -> None` | Emit event to all subscribers of its type. |
| `clear` | `(event_type: type[Event] \| None = None) -> None` | Clear listeners. None = clear all. |

### Usage

```python
bus = EventBus()
bus.on(PlayerDiedEvent, lambda e: print(f"{e.player_name} died"))
bus.emit(PlayerDiedEvent(player_name="Hero", killer_name="Boss"))
bus.off(PlayerDiedEvent, callback_ref)
```

---

## Function: `get_event_bus`

**File**: `events.py`
**Import**: `from engine.core.events import get_event_bus`

```python
get_event_bus() -> EventBus
```

Returns the global (singleton) event bus. Created on first access.
