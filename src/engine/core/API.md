# engine.core -- API Reference

## Class: `Lifecycle`

**File**: `lifecycle.py`
**Import**: `from engine.core import Lifecycle`

Base class defining game object lifecycle hooks. Component inherits from this.
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
| `on_fixed_update` | `(fixed_dt: float) -> None` | 0~N times per frame at fixed interval (default 1/50s). `fixed_dt` is always `fixed_timestep`. |
| `on_update` | `(dt: float) -> None` | Once per frame. `dt` = seconds since last frame (variable). |
| `on_late_update` | `(dt: float) -> None` | Once per frame, after ALL `on_update` calls across all entities. |
| `on_draw` | `(renderer: Renderer) -> None` | Every frame during render phase. |
| `on_destroy` | `() -> None` | When component is removed or entity is destroyed. |

### fixed_update vs update

- `on_fixed_update(fixed_dt)`: 고정 간격으로 호출 (기본 1/50초 = 20ms). 물리, 충돌 처리 등 결정적 시뮬레이션에 사용. 프레임이 느리면 한 프레임에 여러 번 호출되어 따라잡음.
- `on_update(dt)`: 매 프레임 1회. `dt`는 가변. 입력 처리, 일반 게임 로직에 사용.

---

## Class: `Game`

**File**: `game.py`
**Import**: `from engine.core import Game`

Main entry point. Creates App (SDL2) and runs the game loop internally.
Developers do NOT write a while loop -- `Game.run()` handles it.

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

| Property | Type | Description |
|---|---|---|
| `app` | `App` | The underlying SDL2 app (window, renderer, input, clock) |
| `scenes` | `SceneManager` | Scene stack manager |
| `width` | `int` | Window width |
| `height` | `int` | Window height |

### Methods

| Method | Signature | Description |
|---|---|---|
| `run` | `(initial_scene: Scene) -> None` | Start the game loop. Blocks until `quit()` is called or window is closed. |
| `quit` | `() -> None` | Stop the game loop. |

### Usage

```python
game = Game(title="My Game", width=800, height=600)
game.run(MyScene())  # blocks here until game ends
```

---

## Class: `App`

**File**: `app.py`
**Import**: `from engine.core import App`

Low-level SDL2 wrapper. Created internally by `Game`.
Access via `game.app` or `current_app()`.

### Properties

| Property | Type | Description |
|---|---|---|
| `running` | `bool` | False after quit() or window close |
| `clock` | `Clock` | Frame timing |
| `keyboard` | `Keyboard` | Keyboard state |
| `mouse` | `Mouse` | Mouse state |
| `renderer` | `Renderer` | Draw command interface |

### Methods

| Method | Signature | Description |
|---|---|---|
| `poll_events` | `() -> None` | Poll SDL events, update input state |
| `quit` | `() -> None` | Set running = False |
| `destroy` | `() -> None` | Cleanup SDL resources |

---

## Function: `current_app`

```python
current_app() -> App
```

Returns the active App instance. Use inside Components to access input, clock, etc.

```python
class MyComponent(Component):
    def on_update(self, dt):
        kb = current_app().keyboard
        if kb.is_pressed(Key.SPACE):
            # ...
```

---

## Class: `Clock`

**File**: `clock.py`
**Import**: `from engine.core import Clock`

High-resolution frame timing via SDL2.

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `dt` | `float` | no | Last frame delta time in seconds |
| `fps` | `float` | no | Smoothed FPS (updated every 0.5s) |
| `total_time` | `float` | no | Total elapsed seconds |
| `frame_count` | `int` | no | Total frames ticked |
| `target_fps` | `int` | yes | FPS cap target |

### Methods

| Method | Signature | Returns |
|---|---|---|
| `tick` | `() -> float` | Delta time in seconds |
