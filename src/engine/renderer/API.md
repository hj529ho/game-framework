# engine.renderer — API Reference

## Class: `Renderer`

**File**: `renderer.py`
**Import**: `from engine.renderer import Renderer`

Deferred draw queue backed by SDL2 `SDL_Renderer`. Draw commands are collected during the frame, sorted by layer, and executed in `end_frame()`.

### Constructor

```python
Renderer(sdl_renderer: SDL_Renderer)
```

Created internally by `App`. Access via `app.renderer`.

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `sdl_renderer` | `SDL_Renderer` | no | Raw SDL2 renderer handle |
| `clear_color` | `Color` | yes | Background color used in `begin_frame()` |

### Frame Methods

| Method | Signature | Description |
|---|---|---|
| `begin_frame` | `()` | Clear draw queue, clear screen with `clear_color` |
| `end_frame` | `()` | Sort queue by layer, execute all draw commands, present frame (`SDL_RenderPresent`) |

### Draw Methods

All draw methods accept a `layer: int` parameter (default `0`). Lower layers are drawn first (behind). Within the same layer, draw order matches call order.

#### `draw_rect`

```python
draw_rect(
    x: float, y: float, width: float, height: float,
    color: Color,
    filled: bool = True,
    layer: int = 0,
) → None
```

Draw a rectangle. `filled=False` draws outline only.

#### `draw_line`

```python
draw_line(
    start: Vector2,
    end: Vector2,
    color: Color,
    layer: int = 0,
) → None
```

Draw a line between two points.

#### `draw_texture`

```python
draw_texture(
    texture: SDL_Texture,
    x: float, y: float,
    width: int | None = None,   # None = use texture's native width
    height: int | None = None,  # None = use texture's native height
    angle: float = 0.0,         # rotation in degrees
    layer: int = 0,
) → None
```

Draw an SDL texture. If width/height are None, queries texture size via `SDL_QueryTexture`.

### Layer Ordering

```
layer -1  ← drawn first (background)
layer  0  ← default
layer  1  ← drawn last (foreground)
```

Within the same layer, commands execute in the order they were enqueued (stable sort).

---

## Class: `Color`

**File**: `color.py`
**Import**: `from engine.renderer import Color`

RGBA color. No SDL2 dependency — pure Python.

### Constructor

```python
Color(r: int, g: int, b: int, a: int = 255)
```

### Fields

| Field | Type | Range | Description |
|---|---|---|---|
| `r` | `int` | 0–255 | Red |
| `g` | `int` | 0–255 | Green |
| `b` | `int` | 0–255 | Blue |
| `a` | `int` | 0–255 | Alpha (255 = opaque) |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `to_tuple` | `()` | `tuple[int, int, int, int]` | `(r, g, b, a)` |
| `lerp` | `(other: Color, t: float)` | `Color` | Interpolate between colors |
| `with_alpha` | `(a: int)` | `Color` | New color with different alpha |

### Named Constants (class attributes)

| Name | Value |
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
**Import**: `from engine.renderer import SpriteRenderer`
**Inherits**: `Component`

Component that renders an image at the entity's position. Auto-loads via ResourceManager.

### Constructor

```python
SpriteRenderer(image: str = "", layer: int = 0)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `image` | `str` | yes | Image file path (relative to assets). Setting triggers reload. |
| `width` | `int` | no | Texture width in pixels |
| `height` | `int` | no | Texture height in pixels |
| `layer` | `int` | yes | Render layer (default 0) |
| `anchor` | `Vector2` | yes | Anchor point. (0,0)=top-left, (0.5,0.5)=center. Default: center. |
| `flip_x` | `bool` | yes | Horizontal flip |
| `flip_y` | `bool` | yes | Vertical flip |

Respects entity's `scale` and `rotation`.

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
**Import**: `from engine.renderer import TextRenderer`
**Inherits**: `Component`

Component that renders text at the entity's position. Rebuilds texture only when text/font/color changes.

### Constructor

```python
TextRenderer(
    text: str = "",
    font: str = "",        # TTF font path
    font_size: int = 16,
    color: Color | None = None,  # default: Color.WHITE
    layer: int = 0,
)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `text` | `str` | yes | Text content. Changing triggers rebuild. |
| `font` | `str` | yes | Font file path. Changing triggers rebuild. |
| `font_size` | `int` | yes | Font size in pt. Changing triggers rebuild. |
| `color` | `Color` | yes | Text color. Changing triggers rebuild. |
| `layer` | `int` | yes | Render layer |
| `anchor` | `Vector2` | yes | Anchor point. Default: (0,0) top-left. |
| `width` | `int` | no | Rendered text width |
| `height` | `int` | no | Rendered text height |

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

# Update text dynamically in another component:
class FPSCounter(Component):
    def on_update(self, dt):
        text = self.entity.get_component(TextRenderer)
        text.text = f"FPS: {int(current_app().clock.fps)}"
```
