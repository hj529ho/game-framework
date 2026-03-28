# Core Module

The `engine.core` module provides the foundational classes that power the engine:
`Lifecycle` (the base class for all hook-based behavior), `Game` (the entry
point that runs the loop), `App` (the low-level SDL2 wrapper), and `Clock`
(frame timing). It also provides the `current_app()` function for accessing the
active application from anywhere in your code.

---

## Lifecycle

`Lifecycle` is the base class that defines the hook methods called by the engine
each frame. `Component` inherits from `Lifecycle`. You do not use `Lifecycle`
directly -- you subclass `Component` and override the hooks you need.

### Hook order

```
First frame only:
  on_awake()        -- when component is added to entity via add_component()
  on_start()        -- before first on_update (all components on entity are awake)

Every frame:
  on_update(dt)       -- game logic, input
  on_late_update(dt)  -- post-update (camera, constraints)

Render phase:
  on_draw(renderer)   -- visual output

Cleanup:
  on_destroy()        -- when component or entity is removed
```

### Hook reference

| Hook | Signature | When Called |
|---|---|---|
| `on_awake` | `() -> None` | Immediately when `entity.add_component()` is called |
| `on_start` | `() -> None` | Once, before first `on_update`. All sibling components are awake. |
| `on_update` | `(dt: float) -> None` | Every frame. `dt` = seconds since last frame. |
| `on_late_update` | `(dt: float) -> None` | Every frame, after ALL `on_update` calls across all entities. |
| `on_draw` | `(renderer: Renderer) -> None` | Every frame during render phase. |
| `on_destroy` | `() -> None` | When component is removed or entity is destroyed. |

### When to use each hook

- **`on_awake`**: Initialize fields that depend on the entity reference (e.g.,
  reading the entity's position, setting default colors). Called immediately when
  the component is added, before the entity enters the world.

- **`on_start`**: Initialize logic that depends on other components on the same
  entity (e.g., getting a reference to a sibling component). Called once, on the
  first frame after the entity is added to the world.

- **`on_update`**: Main game logic -- input handling, movement, AI, timers.
  Called every frame with the delta time.

- **`on_late_update`**: Post-update logic that depends on all positions being
  finalized -- camera follow, constraints, UI sync. Called every frame after all
  `on_update` calls across all entities have finished.

- **`on_draw`**: Visual output. Use the `renderer` parameter to draw shapes,
  textures, and lines.

- **`on_destroy`**: Cleanup when the component is removed or its entity is
  destroyed. Release resources, unsubscribe from events.

---

## Game

`Game` is the main entry point for your application. It creates the `App`
(SDL2 window, renderer, input, clock) and runs the game loop internally.
Developers do **not** write a `while` loop -- `Game.run()` handles everything.

### Constructor

```python
from engine import Game, Color

game = Game(
    title="My Game",          # Window title bar text
    width=800,                 # Window width in pixels
    height=600,                # Window height in pixels
    fps=60,                    # Target frames per second
    vsync=True,                # Enable vertical sync
    resizable=False,           # Allow window resizing
    clear_color=Color(30, 30, 30),  # Background color (default: dark gray)
)
```

All parameters have defaults, so `Game()` alone creates an 800x600 window
titled "Game" at 60 FPS with vsync enabled.

### Properties

| Property | Type | Description |
|---|---|---|
| `game.app` | `App` | The underlying SDL2 app (window, renderer, input, clock) |
| `game.scenes` | `SceneManager` | The scene stack manager |
| `game.width` | `int` | Window width in pixels |
| `game.height` | `int` | Window height in pixels |

### Methods

#### `run(initial_scene)`

```python
game.run(MyScene())
```

Start the game loop with the given scene. This method **blocks** until
`quit()` is called or the window is closed. Internally, it:

1. Pushes the initial scene onto the SceneManager stack.
2. Runs the frame loop (poll events, tick clock, update scene, draw scene).
3. On exit, clears all scenes and destroys SDL2 resources.

#### `quit()`

```python
game.quit()
```

Stops the game loop. The current frame completes, then `run()` returns.

### Lifecycle per frame

```
Game.run() loop:
  1. App.poll_events()               -- SDL event polling, input state update
  2. Clock.tick()                    -- delta time calculation
  3. Scene.update(dt):
     a. World._process_additions()   -- add queued entities
     b. Component.on_start()         -- first frame only, for new components
     c. Component.on_update(dt)      -- every frame
     d. Component.on_late_update(dt) -- after all updates
     e. World._process_removals()    -- remove queued entities + on_destroy
  4. Renderer.begin_frame()          -- clear screen
  5. Scene.draw(renderer):
     a. Component.on_draw(renderer)  -- for all active components
  6. Renderer.end_frame()            -- sort by layer, execute, present
  7. SceneManager.process_pending()  -- scene transitions
```

### Usage

```python
import engine

class GameScene(engine.Scene):
    def on_enter(self):
        player = engine.Entity("Player")
        player.add_component(PlayerMovement())
        player.add_component(PlayerRenderer())
        self.add(player)

game = engine.Game(title="My Game", width=800, height=600)
game.run(GameScene())  # blocks here until game ends
```

---

## App

`App` is the low-level SDL2 wrapper. It is created internally by `Game`. You
access it via `game.app` or from within Components via `current_app()`.

### What App creates

When `App` is instantiated, it:

1. Initializes SDL2 (`SDL_Init` for video and audio).
2. Creates an SDL2 window with the title and dimensions you specify.
3. Creates a hardware-accelerated SDL2 renderer (with optional vsync).
4. Creates the `Clock`, `Keyboard`, `Mouse`, and `Renderer` subsystems.
5. Registers itself as the global "current app" so Components can access it.

### Properties

| Property | Type | Description |
|---|---|---|
| `app.width` | `int` | Window width in pixels (read-only) |
| `app.height` | `int` | Window height in pixels (read-only) |
| `app.running` | `bool` | `True` until `quit()` is called or the window is closed |
| `app.clock` | `Clock` | The frame timing subsystem |
| `app.keyboard` | `Keyboard` | The keyboard input subsystem |
| `app.mouse` | `Mouse` | The mouse input subsystem |
| `app.renderer` | `Renderer` | The deferred draw queue renderer |

### Methods

#### `poll_events()`

Called internally by `Game.run()` each frame. Polls all pending SDL2 events,
updates keyboard and mouse state, and detects window close.

#### `quit()`

Sets `app.running` to `False`. The game loop exits on the next iteration.

#### `destroy()`

Destroys the SDL2 renderer and window, calls `SDL_Quit()`, and clears the
global `current_app` reference. Called automatically by `Game.run()` on exit.

---

## Clock

`Clock` provides high-resolution frame timing using SDL2's performance counter
(`SDL_GetPerformanceCounter`). It measures the time between frames and sleeps
when necessary to maintain the target frame rate.

### Constructor

```python
from engine import Clock

clock = Clock(target_fps=60)
```

You typically do not create a `Clock` directly. `App` creates one for you,
accessible via `current_app().clock`.

### The `tick()` Method

Called internally by `Game.run()` each frame. It:

1. Measures the elapsed time since the last call to `tick()`.
2. If the frame completed faster than `1 / target_fps` seconds, sleeps for the
   remaining time using `SDL_Delay`.
3. Recalculates the actual delta time after sleeping.
4. Accumulates total time and frame count.
5. Updates the smoothed FPS counter (recalculated every 0.5 seconds).
6. Returns the delta time in **seconds** as a float.

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `clock.dt` | `float` | no | Last frame's delta time in seconds |
| `clock.fps` | `float` | no | Smoothed FPS (updated every 0.5 seconds) |
| `clock.total_time` | `float` | no | Total elapsed seconds since the first `tick()` |
| `clock.frame_count` | `int` | no | Total number of frames ticked |
| `clock.target_fps` | `int` | yes | Target FPS for the frame rate cap |

### Understanding delta time

Delta time (`dt`) is the number of seconds that passed since the last frame.
At 60 FPS, `dt` is approximately `0.01667` seconds (1/60th of a second).

The engine passes `dt` to `on_update` and `on_late_update` automatically. Always
multiply velocities and time-dependent values by `dt`:

```python
class Movement(engine.Component):
    def on_start(self):
        self.speed = 200.0

    def on_update(self, dt):
        # Move 200 pixels per second, regardless of frame rate
        self.transform.translate(engine.Vector2.right() * self.speed * dt)
```

If you omit `dt`, the entity moves 200 pixels per **frame**, which means faster
at higher frame rates and slower at lower frame rates.

### Timing diagram

```
Frame 1          Frame 2          Frame 3
|                |                |
|---game logic---|---game logic---|---game logic---|
|  3 ms          |  8 ms          |  2 ms          |
|---sleep--------|---sleep--------|---sleep--------|
|  13.67 ms      |  8.67 ms       |  14.67 ms      |
|                |                |                |
tick()           tick()           tick()           tick()
dt = ~16.67ms    dt = ~16.67ms    dt = ~16.67ms
     (0.01667s)       (0.01667s)       (0.01667s)
```

At 60 FPS, each frame budget is ~16.67 ms. The clock sleeps for the difference
between the actual work time and the frame budget.

### Changing the frame rate at runtime

You can change the target FPS from within a Component:

```python
class FPSSwitcher(engine.Component):
    def on_update(self, dt):
        kb = engine.current_app().keyboard
        if kb.is_just_pressed(engine.Key.F1):
            engine.current_app().clock.target_fps = 30
        if kb.is_just_pressed(engine.Key.F2):
            engine.current_app().clock.target_fps = 60
        if kb.is_just_pressed(engine.Key.F3):
            engine.current_app().clock.target_fps = 144
```

### Displaying FPS

```python
class FPSDisplay(engine.Component):
    def on_update(self, dt):
        # The fps value updates every 0.5s internally
        print(f"FPS: {engine.current_app().clock.fps:.1f}", end="\r")
```

---

## current_app()

```python
from engine import current_app

app = current_app()
```

Returns the active `App` instance. This is the primary way Components access
input, clock, and other engine subsystems.

### When to use it

**Inside Component lifecycle hooks** (the most common use):

```python
class PlayerMovement(engine.Component):
    def on_update(self, dt):
        kb = engine.current_app().keyboard
        if kb.is_pressed(engine.Key.RIGHT):
            self.transform.translate(engine.Vector2.right() * 200 * dt)
```

**Inside helper functions:**

```python
def is_quit_pressed():
    return engine.current_app().keyboard.is_just_pressed(engine.Key.ESCAPE)
```

### When NOT to use it

- Before creating a `Game` (which creates the `App`). Calling `current_app()`
  before any `App` has been instantiated will raise a `RuntimeError`.

### How it works

When `App.__init__()` completes, it sets a module-level variable
`_current_app = self`. When `App.destroy()` is called, it sets
`_current_app = None`. The `current_app()` function simply returns this
variable (or raises `RuntimeError` if it is `None`).

Only one `App` can exist at a time. Creating a second `App` would overwrite
the reference.

---

## Where to Go Next

| Topic | Document |
|---|---|
| Vectors, rects, transforms, math utilities | [Math](math.md) |
| Keyboard, mouse, input patterns | [Input](input.md) |
| Renderer, draw queue, colors, layers | [Rendering](rendering.md) |
| Entities, components, worlds | [ECS](ecs.md) |
| Scenes and scene management | [Scenes](scene.md) |
