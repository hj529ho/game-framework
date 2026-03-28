# Architecture

This document describes the overall structure of the engine, how its modules
relate to each other, and the design principles that guided its creation.

---

## High-Level Architecture

```
+---------------------------------------------------------------+
|                        Your Game Code                         |
|  (Component subclasses, Scene definitions, game logic)        |
+---------------------------------------------------------------+
        |           |           |           |           |
        v           v           v           v           v
+--------+   +----------+   +-------+   +-----+   +-------+
|  core  |   | renderer |   | input |   | ecs |   | scene |
|--------|   |----------|   |-------|   |-----|   |-------|
|Lifecycl|   | Renderer |   | Key   |   |Entity|  | Scene |
| Game   |   | Color    |   |Mouse  |   |Comp. |  |Scene  |
| App    |   |          |   |Button |   |World |  |Manager|
| Clock  |   |          |   |Keybd  |   |      |  |       |
|curr_app|   |          |   |       |   |      |  |       |
+--------+   +----------+   +-------+   +-----+   +-------+
        |           |           |
        v           v           v
+---------------------------------------------------------------+
|                    engine.math                                |
|  Vector2, Rect, Circle, Transform2D, utils                   |
+---------------------------------------------------------------+
        |
        v
+---------------------------------------------------------------+
|                 PySDL2  (Python bindings)                     |
+---------------------------------------------------------------+
        |
        v
+---------------------------------------------------------------+
|                 SDL2  (native C library)                      |
|         windowing | rendering | input | audio                 |
+---------------------------------------------------------------+
```

---

## Module Dependency Graph

The arrows below mean "depends on" (imports from).

```
scene --------> ecs --------> math
  |               |              ^
  |               v              |
  +----------> renderer --------+
                  |
                  v
                 math

core ---------> renderer
  |               |
  |               v
  +-----------> input --------> math
  |
  +-----------> math

input ---------> math  (Mouse uses Vector2 for position)

ecs -----------> math  (Entity uses Transform2D, Vector2)
  |
  +-----------> core   (Component inherits Lifecycle)
```

Simplified dependency order (bottom = no engine dependencies):

```
Layer 3:  scene
Layer 2:  ecs, core
Layer 1:  renderer, input
Layer 0:  math  (no engine dependencies, only stdlib + PySDL2 for utils)
```

The `math` module is the foundation. It has no dependencies on other engine
modules. Everything else builds upward from there.

---

## Module Summary

| Module | Purpose | Key Classes |
|---|---|---|
| `engine.math` | 2D math primitives and utility functions | `Vector2`, `Rect`, `Circle`, `Transform2D`, `utils` |
| `engine.input` | Keyboard and mouse state tracking | `Key`, `MouseButton`, `Keyboard`, `Mouse` |
| `engine.renderer` | Deferred draw queue backed by SDL2 | `Renderer`, `Color` |
| `engine.core` | Game entry point, app wrapper, lifecycle base, timing | `Lifecycle`, `Game`, `App`, `Clock`, `current_app()` |
| `engine.ecs` | Unity-like entity/component system with a world container | `Entity`, `Component`, `World` |
| `engine.scene` | Scene management with a stack-based transition model | `Scene`, `SceneManager` |

All public symbols are re-exported from the top-level `engine` package, so you
can write `import engine` and access everything as `engine.Game`, `engine.Vector2`,
etc.

---

## Design Philosophy

### 1. Engine-Managed Lifecycle

The engine owns the main loop. `Game.run()` runs the frame lifecycle internally.
You define behavior by writing `Component` subclasses with lifecycle hooks and
`Scene` subclasses with setup/teardown hooks. The engine calls them in the
correct order each frame. This design:

- Guarantees correct lifecycle ordering (start before update, update before draw,
  late update after all updates).
- Lets you focus on game logic instead of loop plumbing.
- Provides a consistent, predictable execution model across all projects.

```python
# You define components with behavior hooks:
class PlayerMovement(engine.Component):
    def on_update(self, dt):
        kb = engine.current_app().keyboard
        if kb.is_pressed(engine.Key.RIGHT):
            self.transform.translate(engine.Vector2.right() * 200 * dt)

# You define scenes that set up the world:
class GameScene(engine.Scene):
    def on_enter(self):
        player = engine.Entity("Player")
        player.add_component(PlayerMovement())
        self.add(player)

# The engine runs everything:
game = engine.Game(title="My Game", width=800, height=600)
game.run(GameScene())
```

### 2. Unity-Like Component Pattern

The engine follows a component-based architecture inspired by Unity:

- **`Lifecycle`** is the base class that defines the hook methods: `on_awake`,
  `on_start`, `on_update`, `on_late_update`, `on_draw`, `on_destroy`.
- **`Component`** inherits from `Lifecycle`. You subclass `Component` to define
  behavior and attach instances to entities.
- **`Entity`** is a pure container (like Unity's `GameObject`). It holds a
  `Transform2D`, a list of `Component` instances, tags, and child entities.
  Entity itself has **no** lifecycle hooks and **no** behavior -- all logic lives
  in Components.

This separation means:

- Game logic is modular and composable. You can attach any combination of
  Components to any Entity.
- Entities are lightweight containers that gain behavior only through their
  attached Components.
- You query the world for entities that have specific component types.

### 3. SDL2 Backend

All windowing, rendering, and input is handled by SDL2 through PySDL2. The
engine does not abstract SDL2 away completely -- it wraps it into convenient
Python classes while keeping the raw SDL2 handles accessible when you need them
(for example, `renderer.sdl_renderer` gives you the `SDL_Renderer` pointer).

This means:

- You get hardware-accelerated 2D rendering.
- You can drop down to raw SDL2 calls when the engine's API is not enough.
- The engine does not need to implement its own windowing or event system.

### 4. Deferred Draw Queue

The renderer does **not** draw immediately when you call `draw_rect()` or
`draw_line()`. Instead, it collects all draw commands into a queue. When
`end_frame()` is called, the queue is sorted by layer number and then executed
in order. This approach:

- Lets Components issue draw calls in any order during the frame, without
  worrying about which layer something ends up on.
- Gives the renderer the freedom to batch or reorder commands in the future.
- Makes it easy to implement a layer system (backgrounds behind sprites behind
  UI).

```
Your code:                         Internal queue:
  draw_rect(... layer=1)            [layer=1, order=0, draw_rect]
  draw_rect(... layer=0)            [layer=0, order=1, draw_rect]
  draw_line(... layer=0)            [layer=0, order=2, draw_line]

After sort in end_frame():
  [layer=0, order=1, draw_rect]    <-- drawn first
  [layer=0, order=2, draw_line]    <-- drawn second (same layer, later order)
  [layer=1, order=0, draw_rect]    <-- drawn last (higher layer)
```

### 5. Stack-Based Scenes

The `SceneManager` uses a stack to manage scene transitions. This maps naturally
to common game patterns:

- **Push** a pause menu on top of the game scene (game stays in memory).
- **Pop** the pause menu to resume the game.
- **Replace** the current scene to transition from the title screen to gameplay.
- **Clear** the entire stack to return to a clean state.

Scenes receive lifecycle hooks (`on_enter`, `on_exit`, `on_pause`, `on_resume`)
so they can set up and tear down resources at the right time.

---

## Data Flow: One Frame

Here is what happens during a single frame of your game, as managed by
`Game.run()`:

```
+------------------------------------------------------------------+
| 1. POLL EVENTS                                                    |
|    App.poll_events()                                              |
|      - Swap input buffers (previous <- current)                   |
|      - Read all pending SDL2 events                               |
|      - Update keyboard state (key down/up)                        |
|      - Update mouse state (position, buttons, scroll)             |
|      - Detect window close -> set app.running = False             |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
| 2. TICK CLOCK                                                     |
|    Clock.tick()                                                   |
|      - Measure time since last frame                              |
|      - Sleep if frame was faster than target FPS                  |
|      - Return delta time in seconds                               |
|      - Update FPS counter (every 0.5s)                            |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
| 3. UPDATE                                                         |
|    Scene.update(dt)                                               |
|      - World._process_additions()  -- add queued entities         |
|      - Component.on_start()        -- first frame only, new comps |
|      - Component.on_update(dt)     -- every frame, all comps      |
|      - Component.on_late_update(dt)-- after all on_update calls   |
|      - World._process_removals()   -- on_destroy + remove         |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
| 4. BEGIN FRAME                                                    |
|    Renderer.begin_frame()                                         |
|      - Clear the draw queue                                       |
|      - Clear the screen to clear_color                            |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
| 5. DRAW                                                           |
|    Scene.draw(renderer)                                           |
|      - Component.on_draw(renderer) on all active components       |
|      - Each draw call enqueues a command (not executed yet)        |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
| 6. END FRAME                                                      |
|    Renderer.end_frame()                                           |
|      - Sort draw queue by (layer, insertion order)                |
|      - Execute all draw commands (SDL2 render calls)              |
|      - Present frame to screen (SDL_RenderPresent)                |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
| 7. SCENE TRANSITIONS                                              |
|    SceneManager.process_pending()                                 |
|      - Execute any queued push/pop/replace/clear transitions      |
+------------------------------------------------------------------+
```

### Why this order?

- **Events before update**: Input state must be fresh before Components read it.
- **Clock after events**: Delta time measures the full frame-to-frame interval.
- **Update before draw**: Game state must be current before we render it.
- **on_start before on_update**: New components initialize before they run logic.
- **on_late_update after all on_update**: Camera follow, constraints, and other
  post-update logic can rely on all positions being updated.
- **Begin/end frame wrapping draw calls**: The renderer needs a clean queue
  before commands are added, and needs to sort and execute them after all
  commands are enqueued.
- **Scene transitions last**: Transitions happen after the frame is complete, so
  they never interrupt an in-progress update or draw.

---

## File Structure

```
game-framework/
  src/
    engine/
      __init__.py           # Re-exports all public symbols
      core/
        __init__.py
        lifecycle.py        # Lifecycle (base class for hooks)
        game.py             # Game (entry point, runs the loop)
        app.py              # App, current_app()
        clock.py            # Clock
      math/
        __init__.py
        vector2.py          # Vector2
        rect.py             # Rect
        circle.py           # Circle
        transform.py        # Transform2D
        utils.py            # lerp, clamp, remap, inverse_lerp, smoothstep
      input/
        __init__.py
        keys.py             # Key, MouseButton enums
        keyboard.py         # Keyboard
        mouse.py            # Mouse
      renderer/
        __init__.py
        renderer.py         # Renderer
        color.py            # Color
      ecs/
        __init__.py
        entity.py           # Entity
        component.py        # Component (inherits Lifecycle)
        world.py            # World
      scene/
        __init__.py
        scene.py            # Scene
        scene_manager.py    # SceneManager
  examples/
    minimal.py              # Component pattern demo
    scene_demo.py           # Scene switching demo
  tests/
    ...
  pyproject.toml            # Build config, dependencies
```

---

## Where to Go Next

| Topic | Document |
|---|---|
| Installation and first program | [Getting Started](getting-started.md) |
| Game, App, Clock, and the lifecycle | [Core](core.md) |
| Vectors, rects, transforms, math utilities | [Math](math.md) |
| Keyboard, mouse, input patterns | [Input](input.md) |
| Renderer, draw queue, colors, layers | [Rendering](rendering.md) |
| Entities, components, worlds | [ECS](ecs.md) |
| Scenes and scene management | [Scenes](scene.md) |
