# engine.renderer -- API Reference

## Class: `Renderer`

**File**: `renderer.py`
**Import**: `from engine.renderer.renderer import Renderer`

Deferred draw queue backed by SDL2 `SDL_Renderer`. Draw commands are collected during the frame, sorted by layer, and executed in `end_frame()`.

Created internally by `App`. Access via `current_app().renderer`.

### Constructor

```python
Renderer(sdl_renderer: SDL_Renderer)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `sdl_renderer` | `SDL_Renderer` | no | Raw SDL2 renderer handle |
| `clear_color` | `Color` | yes | Background color used in `begin_frame()`. Default: `Color(30, 30, 30)`. |

### Frame Methods

| Method | Signature | Description |
|---|---|---|
| `begin_frame` | `() -> None` | Clear draw queue and order counter. Clear screen with `clear_color`. |
| `end_frame` | `() -> None` | Sort queue by `(layer, insertion_order)`, execute all draw commands, call `SDL_RenderPresent`. |

### Draw Methods

All draw methods accept `layer: int` (default `0`) and `world_space: bool` (default `True`).

- `layer` controls draw order: lower layers draw first (behind). Same-layer commands draw in call order (stable sort).
- `world_space`: when `True`, coordinates are transformed through the active `Camera2D` (if any). When `False`, coordinates are screen-space (unaffected by camera).

#### `draw_rect`

```python
draw_rect(
    x: float, y: float, width: float, height: float,
    color: Color,
    filled: bool = True,
    layer: int = 0,
    world_space: bool = True,
) -> None
```

Draw a rectangle. `filled=True` draws a solid rect; `filled=False` draws outline only.

#### `draw_line`

```python
draw_line(
    start: Vector2,
    end: Vector2,
    color: Color,
    layer: int = 0,
    world_space: bool = True,
) -> None
```

Draw a line between two points.

#### `draw_circle`

```python
draw_circle(
    center: Vector2,
    radius: float,
    color: Color,
    filled: bool = True,
    layer: int = 0,
    world_space: bool = True,
) -> None
```

Draw a circle using the midpoint circle algorithm. `filled=True` fills the circle; `filled=False` draws outline only.

#### `draw_polygon`

```python
draw_polygon(
    points: list[Vector2],
    color: Color,
    layer: int = 0,
    world_space: bool = True,
) -> None
```

Draw a closed polygon outline (connects the last point back to the first). Requires at least 2 points.

#### `draw_texture`

```python
draw_texture(
    texture: SDL_Texture,
    x: float, y: float,
    width: int | None = None,   # None = use texture's native width
    height: int | None = None,  # None = use texture's native height
    angle: float = 0.0,         # rotation in degrees
    layer: int = 0,
    world_space: bool = True,
) -> None
```

Draw an SDL texture. If `width`/`height` are None, queries texture size via `SDL_QueryTexture`. Supports rotation via `SDL_RenderCopyEx`.

### Layer Ordering

```
layer -1  -- drawn first (background)
layer  0  -- default
layer  1  -- drawn on top (foreground)
layer 1000 -- UI elements (used by ui module)
layer 1001 -- UI text / images (used by ui module)
layer 9999 -- transition overlays
```

Within the same layer, commands execute in the order they were enqueued (stable sort).

---

## Class: `Color`

**File**: `color.py`
**Import**: `from engine.renderer.color import Color`

RGBA color with `__slots__`. Hashable and equality-comparable.

### Constructor

```python
Color(r: int, g: int, b: int, a: int = 255)
```

### Fields

| Field | Type | Range | Writable | Description |
|---|---|---|---|---|
| `r` | `int` | 0--255 | yes | Red |
| `g` | `int` | 0--255 | yes | Green |
| `b` | `int` | 0--255 | yes | Blue |
| `a` | `int` | 0--255 | yes | Alpha (255 = opaque) |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `to_tuple` | `()` | `tuple[int, int, int, int]` | `(r, g, b, a)` |
| `lerp` | `(other: Color, t: float)` | `Color` | Linear interpolation between colors |
| `with_alpha` | `(a: int)` | `Color` | New Color with replaced alpha channel |

### Named Constants (class attributes)

| Name | Value (r, g, b, a) |
|---|---|
| `Color.WHITE` | `(255, 255, 255, 255)` |
| `Color.BLACK` | `(0, 0, 0, 255)` |
| `Color.RED` | `(255, 0, 0, 255)` |
| `Color.GREEN` | `(0, 255, 0, 255)` |
| `Color.BLUE` | `(0, 0, 255, 255)` |
| `Color.YELLOW` | `(255, 255, 0, 255)` |
| `Color.CYAN` | `(0, 255, 255, 255)` |
| `Color.MAGENTA` | `(255, 0, 255, 255)` |
| `Color.ORANGE` | `(255, 165, 0, 255)` |
| `Color.GRAY` | `(128, 128, 128, 255)` |
| `Color.DARK_GRAY` | `(64, 64, 64, 255)` |
| `Color.LIGHT_GRAY` | `(192, 192, 192, 255)` |
| `Color.TRANSPARENT` | `(0, 0, 0, 0)` |

---

## Class: `SpriteRenderer`

**File**: `sprite.py`
**Import**: `from engine.renderer.sprite import SpriteRenderer`
**Inherits**: `Component`

Component that renders an image at the entity's position. Auto-loads via `ResourceManager`.

### Constructor

```python
SpriteRenderer(image: str = "", layer: int = 0)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `image` | `str` | yes | Image file path (relative to assets). Setting clears the cached texture (reloads on next draw). |
| `width` | `int` | no | Loaded texture width in pixels |
| `height` | `int` | no | Loaded texture height in pixels |
| `layer` | `int` | yes | Render layer (default 0) |
| `anchor` | `Vector2` | yes | Anchor point. `(0,0)` = top-left, `(0.5,0.5)` = center. Default: `(0.5, 0.5)`. |
| `flip_x` | `bool` | yes | Horizontal flip. Default: `False`. |
| `flip_y` | `bool` | yes | Vertical flip. Default: `False`. |

Respects the entity's `scale` and `rotation`.

### Usage

```python
player = Entity("Player")
sprite = player.add_component(SpriteRenderer("player.png"))
sprite.anchor = Vector2(0.5, 1.0)  # bottom-center
sprite.layer = 1
```

---

## Class: `TextRenderer`

**File**: `text.py`
**Import**: `from engine.renderer.text import TextRenderer`
**Inherits**: `Component`

Component that renders text at the entity's position. Rebuilds the internal SDL texture only when text, font, font_size, or color changes.

### Constructor

```python
TextRenderer(
    text: str = "",
    font: str = "",            # TTF font file path
    font_size: int = 16,
    color: Color | None = None,  # default: Color.WHITE
    layer: int = 0,
)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `text` | `str` | yes | Text content. Changing marks texture for rebuild. |
| `font` | `str` | yes | Font file path. Changing marks texture for rebuild. |
| `font_size` | `int` | yes | Font size in points. Changing marks texture for rebuild. |
| `color` | `Color` | yes | Text color. Changing marks texture for rebuild. |
| `layer` | `int` | yes | Render layer |
| `anchor` | `Vector2` | yes | Anchor point. Default: `(0.0, 0.0)` (top-left). |
| `width` | `int` | no | Rendered text width in pixels |
| `height` | `int` | no | Rendered text height in pixels |

### Lifecycle Hooks Used

- `on_draw(renderer)`: Rebuilds texture if dirty, then draws text at entity position.
- `on_destroy()`: Frees the SDL texture.

### Usage

```python
label = Entity("FPS")
label.position = Vector2(10, 10)
text = label.add_component(TextRenderer(
    text="FPS: 60",
    font="fonts/mono.ttf",
    font_size=14,
    color=Color.GREEN,
))
```

---

## Class: `Camera2D`

**File**: `camera.py`
**Import**: `from engine.renderer.camera import Camera2D`
**Inherits**: `Component`

2D camera component. The camera's position is the entity's position (center of view). The `Renderer` uses the active camera to transform world-space coordinates to screen-space.

### Constructor

```python
Camera2D(viewport_width: int = 800, viewport_height: int = 600)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `viewport_width` | `int` | no | Viewport width in pixels |
| `viewport_height` | `int` | no | Viewport height in pixels |
| `zoom` | `float` | yes | Zoom level. Default: `1.0`. Greater = zoomed in. |
| `follow_target` | `Entity \| None` | yes | Entity to follow. Default: `None`. |
| `follow_speed` | `float` | yes | Lerp speed for following. Default: `5.0`. `<= 0` = instant snap. |
| `follow_offset` | `Vector2` | yes | Offset from follow target. Default: `Vector2.zero()`. |
| `bounds` | `Rect` | no | Visible world-space rectangle (for culling). |

### Static Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `Camera2D.get_active()` | `()` | `Camera2D \| None` | Get the currently active camera. |

### Instance Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `set_active` | `()` | `None` | Set this camera as the active camera. |
| `world_to_screen` | `(world_pos: Vector2)` | `Vector2` | Convert world coordinates to screen coordinates. |
| `screen_to_world` | `(screen_pos: Vector2)` | `Vector2` | Convert screen coordinates to world coordinates. |

### Lifecycle Hooks Used

- `on_awake()`: Sets self as active camera if none exists.
- `on_late_update(dt)`: Follows `follow_target` with lerp smoothing.
- `on_destroy()`: Clears active camera reference if self was active.

### Usage

```python
cam_entity = Entity("Camera")
cam_entity.position = Vector2(400, 300)
camera = cam_entity.add_component(Camera2D(800, 600))
camera.follow_target = player_entity
camera.follow_speed = 5.0
scene.add(cam_entity)
```

---

## Dataclass: `Animation`

**File**: `animated_sprite.py`
**Import**: `from engine.renderer.animated_sprite import Animation`

Defines a named animation sequence from a spritesheet.

| Field | Type | Default | Description |
|---|---|---|---|
| `frames` | `list[int]` | (required) | Frame indices in the spritesheet grid |
| `fps` | `float` | `10.0` | Playback speed (frames per second) |
| `loop` | `bool` | `True` | Whether to loop when finished |

---

## Class: `AnimatedSprite`

**File**: `animated_sprite.py`
**Import**: `from engine.renderer.animated_sprite import AnimatedSprite`
**Inherits**: `Component`

Plays spritesheet animations. The spritesheet is a single image with frames laid out in a grid.

### Constructor

```python
AnimatedSprite(
    image: str = "",
    frame_width: int = 32,
    frame_height: int = 32,
    layer: int = 0,
)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `image` | `str` | yes | Spritesheet image path. Setting clears cached texture. |
| `frame_width` | `int` | no | Width of a single frame in pixels |
| `frame_height` | `int` | no | Height of a single frame in pixels |
| `current_animation` | `str` | no | Name of the currently selected animation |
| `current_frame` | `int` | no | Current frame index in the spritesheet |
| `is_playing` | `bool` | no | Whether animation is currently playing |
| `is_finished` | `bool` | no | True when a non-looping animation has ended |
| `layer` | `int` | yes | Render layer |
| `anchor` | `Vector2` | yes | Anchor point. Default: `(0.5, 0.5)` (center). |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add_animation` | `(name: str, animation: Animation)` | `None` | Register a named animation |
| `play` | `(name: str, restart: bool = False)` | `None` | Play animation by name. No-op if already playing that animation unless `restart=True`. Raises `ValueError` if name not found. |
| `stop` | `()` | `None` | Stop playback at current frame |

### Lifecycle Hooks Used

- `on_update(dt)`: Advances frame timer, handles looping / finish.
- `on_draw(renderer)`: Renders current frame from spritesheet with camera transform, scale, and rotation.

### Usage

```python
anim = entity.add_component(AnimatedSprite("player.png", 32, 32))
anim.add_animation("idle", Animation(frames=[0, 1, 2, 3], fps=8))
anim.add_animation("run", Animation(frames=[4, 5, 6, 7, 8, 9], fps=12))
anim.play("idle")
```
