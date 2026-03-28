# Rendering Module

The `engine.renderer` module provides a deferred draw queue built on top of
SDL2's hardware-accelerated 2D renderer. Instead of drawing immediately, all
draw calls are collected into a queue, sorted by layer, and executed at the end
of the frame.

---

## Core Concept: The Deferred Draw Queue

In a typical immediate-mode renderer, each draw call paints to the screen right
away. This means you must issue draw calls in the correct back-to-front order --
background first, then sprites, then UI.

This engine uses a **deferred** approach instead:

```
Your code during the frame:          Internal draw queue:
                                     (unsorted)
  draw_rect(... layer=2)             [layer=2, order=0]
  draw_rect(... layer=0)             [layer=0, order=1]
  draw_line(... layer=1)             [layer=1, order=2]
  draw_rect(... layer=0)             [layer=0, order=3]

end_frame() sorts by (layer, order):

  Execute: [layer=0, order=1]   <-- background
  Execute: [layer=0, order=3]   <-- background (same layer, later call)
  Execute: [layer=1, order=2]   <-- midground
  Execute: [layer=2, order=0]   <-- foreground
```

This means Components can issue draw calls in **any order** during the frame.
The layer system ensures everything ends up in the right visual order.

---

## Frame Lifecycle

The rendering cycle is managed internally by `Game.run()`. Each frame follows
this sequence:

```
Game.run() internally:
  ... update phase ...
  Renderer.begin_frame()           # Step 1: Clear
  Scene.draw(renderer) ->
    Component.on_draw(renderer)    # Step 2: Components enqueue draw calls
  Renderer.end_frame()             # Step 3: Sort, execute, present
```

### `begin_frame()`

- Clears the internal draw queue.
- Resets the insertion order counter.
- Clears the screen to `clear_color` using `SDL_RenderClear`.

### Component `on_draw` calls (between begin and end)

Each call creates a `_DrawCommand` object containing the layer number, an
insertion order counter, and a closure that performs the actual SDL2 draw call.
The command is appended to the queue. **Nothing is drawn to the screen yet.**

### `end_frame()`

- Sorts the draw queue by `(layer, insertion_order)`.
- Executes each draw command's closure in sorted order.
- Calls `SDL_RenderPresent` to flip the back buffer to the screen.

```
begin_frame()          end_frame()
     |                      |
     |   on_draw() calls    |  sort queue
     |   draw_rect()        |  execute commands
     |   draw_line()        |  SDL_RenderPresent
     |   draw_texture()     |
     |                      |
  clear screen          present to display
  reset queue
```

---

## Drawing Primitives

All drawing happens inside a Component's `on_draw` method, which receives the
`renderer` as a parameter.

### `draw_rect` -- Rectangles

```python
renderer.draw_rect(
    x, y,                # top-left corner position
    width, height,       # dimensions
    color,               # Color instance
    filled=True,         # True = solid, False = outline only
    layer=0,             # draw layer
)
```

**Filled rectangle:**

```python
class BoxRenderer(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(p.x - 50, p.y - 25, 100, 50, engine.Color.BLUE)
```

```
  (x, y)
     +------------------+
     |//////////////////|
     |//////////////////|  50 px
     |//////////////////|
     +------------------+
          100 px
```

**Outline rectangle:**

```python
renderer.draw_rect(100, 100, 200, 150, engine.Color.RED, filled=False)
```

```
  (100, 100)
     +------------------+
     |                  |
     |                  |  150 px
     |                  |
     +------------------+
          200 px
```

### `draw_line` -- Lines

```python
renderer.draw_line(
    start,    # Vector2 start point
    end,      # Vector2 end point
    color,    # Color instance
    layer=0,  # draw layer
)
```

```python
class LineRenderer(engine.Component):
    def on_draw(self, renderer):
        renderer.draw_line(
            engine.Vector2(50, 50),
            engine.Vector2(300, 200),
            engine.Color.GREEN,
        )
```

### `draw_texture` -- Textures (images)

```python
renderer.draw_texture(
    texture,         # SDL_Texture (loaded via SDL2)
    x, y,            # position
    width=None,      # None = use texture's native width
    height=None,     # None = use texture's native height
    angle=0.0,       # rotation in degrees
    layer=0,         # draw layer
)
```

If `width` or `height` is `None`, the renderer queries the texture's native
dimensions using `SDL_QueryTexture`.

```python
class SpriteRenderer(engine.Component):
    def on_awake(self):
        self.texture = load_my_texture()

    def on_draw(self, renderer):
        p = self.position
        # Draw at native size
        renderer.draw_texture(self.texture, p.x, p.y)

        # Draw scaled to 64x64
        renderer.draw_texture(self.texture, p.x, p.y, width=64, height=64)

        # Draw rotated 45 degrees
        renderer.draw_texture(self.texture, p.x, p.y, angle=45.0)
```

---

## The Layer System

Every draw call accepts an optional `layer` parameter (default `0`). Layers
control the visual stacking order:

- **Lower layer numbers** are drawn **first** (behind).
- **Higher layer numbers** are drawn **last** (in front).
- Within the **same layer**, draw commands execute in the order they were called.

```
layer -1:  Background tiles, sky
layer  0:  Game objects, enemies, player  (default)
layer  1:  Foreground effects, particles
layer  2:  HUD, health bars, score
```

### Example: Background behind player behind UI

```python
class BackgroundRenderer(engine.Component):
    def on_draw(self, renderer):
        renderer.draw_rect(0, 0, 800, 600, engine.Color.DARK_GRAY, layer=-1)


class PlayerRenderer(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(p.x - 16, p.y - 16, 32, 32, engine.Color.BLUE, layer=0)


class HUDRenderer(engine.Component):
    def on_awake(self):
        self.health_bar_width = 200

    def on_draw(self, renderer):
        renderer.draw_rect(0, 0, 200, 30, engine.Color(0, 0, 0, 180), layer=2)
        renderer.draw_rect(10, 5, self.health_bar_width, 20, engine.Color.RED, layer=2)
```

Even though these Components may execute their `on_draw` in any order, the layer
numbers ensure the correct visual order:

```
Drawn first (behind)        Drawn last (in front)

  +---------+   +---------+   +---------+
  |DARK_GRAY|   |  BLUE   |   | HUD bar |
  |  sky    |   | (player)|   | (score) |
  | layer=-1|   | layer=0 |   | layer=2 |
  +---------+   +---------+   +---------+
```

### Same-layer ordering

Within a single layer, the draw queue preserves insertion order. This means the
last call within a layer draws on top:

```python
# Both at layer 0, in the same on_draw method
renderer.draw_rect(100, 100, 50, 50, engine.Color.RED)    # drawn first
renderer.draw_rect(120, 120, 50, 50, engine.Color.BLUE)   # drawn second (on top)
```

---

## Color

`Color` is a simple RGBA color class. It is pure Python with no SDL2 dependency.

### Creating colors

```python
from engine import Color

# From RGBA components (0-255)
red = Color(255, 0, 0)          # fully opaque red
red_50 = Color(255, 0, 0, 128)  # 50% transparent red

# Alpha defaults to 255 (fully opaque)
white = Color(255, 255, 255)
```

### Named constants

The `Color` class provides commonly used colors as class attributes:

| Name | RGBA Value |
|---|---|
| `Color.WHITE` | (255, 255, 255, 255) |
| `Color.BLACK` | (0, 0, 0, 255) |
| `Color.RED` | (255, 0, 0, 255) |
| `Color.GREEN` | (0, 255, 0, 255) |
| `Color.BLUE` | (0, 0, 255, 255) |
| `Color.YELLOW` | (255, 255, 0, 255) |
| `Color.CYAN` | (0, 255, 255, 255) |
| `Color.MAGENTA` | (255, 0, 255, 255) |
| `Color.ORANGE` | (255, 165, 0, 255) |
| `Color.GRAY` | (128, 128, 128, 255) |
| `Color.DARK_GRAY` | (64, 64, 64, 255) |
| `Color.LIGHT_GRAY` | (192, 192, 192, 255) |
| `Color.TRANSPARENT` | (0, 0, 0, 0) |

### Methods

#### `to_tuple()` -- Convert to tuple

```python
Color.RED.to_tuple()  # (255, 0, 0, 255)
```

#### `lerp(other, t)` -- Interpolate between colors

Blends smoothly from one color to another. `t=0` returns `self`, `t=1` returns
`other`.

```python
start = Color.RED
end = Color.BLUE

start.lerp(end, 0.0)   # Color(255, 0, 0, 255)    -- pure red
start.lerp(end, 0.5)   # Color(127, 0, 127, 255)   -- purple
start.lerp(end, 1.0)   # Color(0, 0, 255, 255)     -- pure blue
```

**Common use case -- health bar color in a Component:**

```python
class HealthBar(engine.Component):
    def on_draw(self, renderer):
        health_pct = self.current_hp / self.max_hp  # 0.0 to 1.0
        bar_color = engine.Color.RED.lerp(engine.Color.GREEN, health_pct)
        p = self.position
        renderer.draw_rect(p.x - 20, p.y - 30, 40 * health_pct, 4, bar_color, layer=1)
```

#### `with_alpha(a)` -- Create a copy with different alpha

```python
solid_red = Color.RED                    # alpha = 255
ghost_red = Color.RED.with_alpha(128)    # alpha = 128 (50% transparent)
invisible = Color.RED.with_alpha(0)      # alpha = 0 (fully transparent)
```

**Common use case -- fade effect:**

```python
from engine.math.utils import smoothstep

class FadeEffect(engine.Component):
    def on_start(self):
        self.elapsed = 0.0

    def on_update(self, dt):
        self.elapsed += dt

    def on_draw(self, renderer):
        # Fade in over 1 second
        opacity = smoothstep(0, 1, self.elapsed)
        color = engine.Color.WHITE.with_alpha(int(opacity * 255))
        p = self.position
        renderer.draw_rect(p.x - 25, p.y - 25, 50, 50, color)
```

---

## Setting the Background Color

The `clear_color` property on the renderer controls what color the screen is
cleared to at the beginning of each frame (during `begin_frame()`).

```python
# Set during Game creation
game = engine.Game(title="My Game", clear_color=engine.Color(20, 20, 40))

# Or change at runtime from a Component
class DayNightCycle(engine.Component):
    def on_update(self, dt):
        engine.current_app().renderer.clear_color = engine.Color.BLACK
```

The default clear color is `Color(30, 30, 30)` -- a dark gray.

---

## Accessing the Raw SDL2 Renderer

If you need to perform SDL2 rendering operations that the engine does not wrap,
you can access the underlying `SDL_Renderer` handle:

```python
sdl_renderer = engine.current_app().renderer.sdl_renderer
```

This gives you the raw SDL2 renderer pointer that you can pass to any PySDL2
function. Use this escape hatch for advanced rendering features like custom
blend modes or render targets.

---

## Complete Example

```python
import engine
from engine.math import utils


class TrailRenderer(engine.Component):
    """Draws a trail of fading rectangles behind the entity."""

    def on_start(self):
        self.trail = []
        self.max_trail = 20

    def on_update(self, dt):
        self.trail.append(self.position.copy())
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

    def on_draw(self, renderer):
        for i, t_pos in enumerate(self.trail):
            alpha = int((i / len(self.trail)) * 200)
            color = engine.Color.CYAN.with_alpha(alpha)
            size = 8 + (i / len(self.trail)) * 16
            renderer.draw_rect(
                t_pos.x - size / 2, t_pos.y - size / 2,
                size, size, color, layer=0,
            )


class PlayerRenderer(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(p.x - 16, p.y - 16, 32, 32, engine.Color.WHITE, layer=1)


class GridBackground(engine.Component):
    def on_draw(self, renderer):
        for x in range(0, 800, 50):
            renderer.draw_line(
                engine.Vector2(x, 0), engine.Vector2(x, 600),
                engine.Color.DARK_GRAY, layer=-1,
            )
        for y in range(0, 600, 50):
            renderer.draw_line(
                engine.Vector2(0, y), engine.Vector2(800, y),
                engine.Color.DARK_GRAY, layer=-1,
            )


class FPSBar(engine.Component):
    def on_draw(self, renderer):
        fps = engine.current_app().clock.fps
        fps_bar_width = utils.remap(fps, 0, 120, 0, 200)
        fps_bar_width = utils.clamp(fps_bar_width, 0, 200)
        renderer.draw_rect(10, 10, fps_bar_width, 20, engine.Color.GREEN, layer=2)
        renderer.draw_rect(10, 10, 200, 20, engine.Color.WHITE, filled=False, layer=2)


class Movement(engine.Component):
    def on_start(self):
        self.speed = 250.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        d = engine.Vector2.zero()
        if kb.is_pressed(engine.Key.LEFT):  d = d + engine.Vector2.left()
        if kb.is_pressed(engine.Key.RIGHT): d = d + engine.Vector2.right()
        if kb.is_pressed(engine.Key.UP):    d = d + engine.Vector2.up()
        if kb.is_pressed(engine.Key.DOWN):  d = d + engine.Vector2.down()
        if d.magnitude > 0:
            self.transform.translate(d.normalized * self.speed * dt)


class QuitOnEscape(engine.Component):
    def on_update(self, dt):
        if engine.current_app().keyboard.is_just_pressed(engine.Key.ESCAPE):
            engine.current_app().quit()


class DemoScene(engine.Scene):
    def on_enter(self):
        # Player with trail
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_component(Movement())
        player.add_component(TrailRenderer())
        player.add_component(PlayerRenderer())
        player.add_component(QuitOnEscape())
        self.add(player)

        # Background grid (on a separate entity)
        bg = engine.Entity("Background")
        bg.add_component(GridBackground())
        self.add(bg)

        # HUD (on a separate entity)
        hud = engine.Entity("HUD")
        hud.add_component(FPSBar())
        self.add(hud)


game = engine.Game(title="Rendering Demo", width=800, height=600)
game.run(DemoScene())
```

This example demonstrates:

- Multiple layers (grid on -1, trail on 0, player on 1, HUD on 2)
- Alpha transparency with `with_alpha()`
- Color constants
- `remap` and `clamp` from the math utilities
- Lines and filled/outlined rectangles
- All rendering done through Component `on_draw` methods

---

## Where to Go Next

| Topic | Document |
|---|---|
| Entities, components, worlds | [ECS](ecs.md) |
| Scenes and scene management | [Scenes](scene.md) |
