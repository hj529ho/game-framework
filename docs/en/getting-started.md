# Getting Started

## What Is This Engine?

This is a lightweight 2D game engine written in Python, built directly on top of
[SDL2](https://www.libsdl.org/) through the
[PySDL2](https://pysdl2.readthedocs.io/) bindings. It provides the fundamental
building blocks you need to make 2D games -- windowing, input handling, a draw
queue renderer, a Unity-like entity/component system, and scene management --
with an engine-managed game loop that lets you focus on gameplay logic.

The engine follows a Unity-like component pattern. You define behavior by writing
`Component` subclasses with lifecycle hooks (`on_update`, `on_draw`, etc.),
attach them to `Entity` containers, group entities into `Scene` objects, and let
the `Game` class run everything for you. There is no user-controlled `while`
loop -- `Game.run()` handles the entire frame lifecycle internally.

### Key technologies

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.11+ | Game logic, engine code |
| Bindings | PySDL2 (>= 0.9.16) | Python-to-SDL2 bridge |
| Native | SDL2 (>= 2.30) | Windowing, rendering, input, audio |
| SDL2 DLLs | pysdl2-dll (>= 2.30.0) | Pre-built SDL2 shared libraries |

---

## Installation

### Prerequisites

- **Python 3.11 or newer**. Check with `python --version`.
- **pip** (comes with Python).

### Step 1 -- Install the engine

From the project root directory, install in editable (development) mode:

```bash
pip install -e .
```

This reads `pyproject.toml` and installs:

- **pysdl2** -- the Python bindings for SDL2
- **pysdl2-dll** -- pre-compiled SDL2 shared libraries for your platform

If you prefer a one-time install without editable mode:

```bash
pip install .
```

### Step 2 -- Verify the installation

Open a Python prompt and confirm the import works:

```python
import engine
print(engine.__version__)  # should print "0.1.0"
```

### Optional: Install development dependencies

If you plan to run tests or use the linter:

```bash
pip install -e ".[dev]"
```

This adds `pytest`, `pytest-cov`, and `ruff`.

---

## Your First Program: Hello World

Let us create a window with a colored rectangle. Create a file called
`hello.py` anywhere on your system:

```python
import engine


class HelloBox(engine.Component):
    """Draws a blue rectangle in the center of the screen."""

    def on_draw(self, renderer):
        renderer.draw_rect(350, 250, 100, 100, engine.Color.BLUE)


class QuitOnEscape(engine.Component):
    """Quits the game when Escape is pressed."""

    def on_update(self, dt):
        if engine.current_app().keyboard.is_just_pressed(engine.Key.ESCAPE):
            engine.current_app().quit()


class HelloScene(engine.Scene):
    def on_enter(self):
        box = engine.Entity("Box")
        box.add_component(HelloBox())
        box.add_component(QuitOnEscape())
        self.add(box)


game = engine.Game(title="Hello World", width=800, height=600, fps=60)
game.run(HelloScene())
```

Run it:

```bash
python hello.py
```

You should see an 800x600 window with a dark gray background and a blue square
in the center. Press Escape or close the window to exit.

### What each part does

```
engine.Game(...)          Create the Game, which internally creates the SDL2
                          window, renderer, clock, and input systems.

engine.Component          Base class for all behavior. Override lifecycle hooks
                          (on_update, on_draw, etc.) to define what happens.

engine.Entity             A container for Components. Has a Transform (position,
                          rotation, scale) but no behavior of its own.

engine.Scene              Owns a World of entities. Override on_enter() to set up
                          the scene, on_exit() to tear it down.

game.run(scene)           Start the engine-managed game loop. Blocks until
                          quit() is called or the window is closed. The engine
                          handles polling events, ticking the clock, calling
                          component hooks, and rendering -- all automatically.
```

---

## The Engine-Managed Game Loop

The engine provides a `Game` class that runs the loop for you. You do **not**
write a `while` loop. Instead, you define behavior through Component lifecycle
hooks and Scene hooks, and the engine calls them in the correct order each frame.

Here is the frame lifecycle managed by `Game.run()`:

```
+------------------------------------------------------------------+
|  game = Game(...)            # create the SDL2 app               |
|  game.run(scene)             # engine takes over                 |
|                                                                  |
|  Per frame (managed internally):                                 |
|    1. App.poll_events()       -- SDL event polling, input update |
|    2. Clock.tick()            -- delta time calculation           |
|    3. Scene.update(dt):                                          |
|       a. World adds queued entities                              |
|       b. Component.on_start() -- first frame only, new comps     |
|       c. Component.on_update(dt) -- every frame                  |
|       d. Component.on_late_update(dt) -- after all updates       |
|       e. World removes queued entities + on_destroy              |
|    4. Renderer.begin_frame()  -- clear screen                    |
|    5. Scene.draw(renderer):                                      |
|       a. Component.on_draw(renderer) -- for all active comps     |
|    6. Renderer.end_frame()    -- sort by layer, present          |
|    7. SceneManager.process_pending() -- scene transitions        |
|                                                                  |
|  After loop exits:                                               |
|    - All scenes are cleared (on_exit called)                     |
|    - SDL2 resources are destroyed                                |
+------------------------------------------------------------------+
```

### Why engine-managed?

1. **Correctness** -- The engine guarantees the right call order every frame.
   `on_start` always runs before `on_update`. `on_late_update` always runs after
   all `on_update` calls. Draw always happens after update.
2. **Simplicity** -- You focus on writing Components with game logic. The engine
   handles the plumbing.
3. **Consistency** -- Every project follows the same lifecycle pattern, making
   code easier to understand and share.

### Delta time

The engine passes delta time (`dt`) to `on_update` and `on_late_update`
automatically. Use it to make movement frame-rate independent:

```python
# Wrong -- speed depends on frame rate
self.position = self.position + engine.Vector2.right() * 5

# Right -- speed is consistent regardless of frame rate
self.position = self.position + engine.Vector2.right() * 300 * dt  # 300 pixels per second
```

---

## A More Complete Example: Moving Rectangle

```python
import engine


class Movement(engine.Component):
    """Handles keyboard movement with normalized diagonal speed."""

    def on_start(self):
        self.speed = 300.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        direction = engine.Vector2.zero()

        if kb.is_pressed(engine.Key.LEFT) or kb.is_pressed(engine.Key.A):
            direction = direction + engine.Vector2.left()
        if kb.is_pressed(engine.Key.RIGHT) or kb.is_pressed(engine.Key.D):
            direction = direction + engine.Vector2.right()
        if kb.is_pressed(engine.Key.UP) or kb.is_pressed(engine.Key.W):
            direction = direction + engine.Vector2.up()
        if kb.is_pressed(engine.Key.DOWN) or kb.is_pressed(engine.Key.S):
            direction = direction + engine.Vector2.down()

        if direction.magnitude > 0:
            self.transform.translate(direction.normalized * self.speed * dt)

        # Clamp to window bounds
        from engine.math import utils
        app = engine.current_app()
        self.position = engine.Vector2(
            utils.clamp(self.position.x, 25, app.width - 25),
            utils.clamp(self.position.y, 25, app.height - 25),
        )


class BoxRenderer(engine.Component):
    """Draws a colored rectangle at the entity's position."""

    def on_awake(self):
        self.color = engine.Color.BLUE
        self.size = 50

    def on_draw(self, renderer):
        p = self.position
        half = self.size / 2
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size, self.color)


class QuitOnEscape(engine.Component):
    def on_update(self, dt):
        if engine.current_app().keyboard.is_just_pressed(engine.Key.ESCAPE):
            engine.current_app().quit()


class GameScene(engine.Scene):
    def on_enter(self):
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_component(Movement())
        player.add_component(BoxRenderer())
        player.add_component(QuitOnEscape())
        self.add(player)


game = engine.Game(title="Moving Rectangle", width=800, height=600)
game.run(GameScene())
```

---

## Running the Included Examples

The project ships with example scripts in the `examples/` directory. To run
them, make sure you have installed the engine first (see Installation above),
then:

```bash
# From the project root directory:
python examples/minimal.py
python examples/scene_demo.py
```

### `examples/minimal.py`

A window with a moving blue rectangle controlled by arrow keys or WASD, plus a
static red obstacle. Press Escape to quit. This demonstrates the Component
pattern with separate Movement, BoxRenderer, and QuitOnEscape components
attached to Entity containers.

### `examples/scene_demo.py`

A two-scene demo. The game scene has a player (blue square) and three enemies
(red squares that oscillate via a SineWave component). Press Space to push a
pause scene on top; press Space again to pop it. Press Escape to quit. This
demonstrates Components, Entities, Scenes, and the SceneManager stack working
together.

---

## Where to Go Next

| Topic | Document |
|---|---|
| Overall architecture and design | [Architecture](architecture.md) |
| Game, App, Clock, and the lifecycle | [Core](core.md) |
| Vectors, rects, transforms, math utilities | [Math](math.md) |
| Keyboard, mouse, input patterns | [Input](input.md) |
| Renderer, draw queue, colors, layers | [Rendering](rendering.md) |
| Entities, components, worlds | [ECS](ecs.md) |
| Scenes and scene management | [Scenes](scene.md) |
