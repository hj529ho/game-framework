# engine.ui -- API Reference

CSS-based UI system with DOM-like element tree, flexbox layout, event bubbling, and stylesheet support.

---

## Units

**File**: `core/units.py`
**Import**: `from engine.ui.core.units import px, pct, auto, Unit, UnitType`

### Enum: `UnitType`

| Member | Description |
|---|---|
| `UnitType.PX` | Fixed pixels |
| `UnitType.PERCENT` | Percentage of parent |
| `UnitType.AUTO` | Computed by layout engine |

### Dataclass: `Unit` (frozen)

```python
@dataclass(frozen=True)
class Unit:
    value: float
    type: UnitType
```

| Method | Signature | Returns | Description |
|---|---|---|---|
| `resolve` | `(parent_size: float)` | `float` | Resolve to pixels. PX returns `value`, PERCENT returns `parent_size * value / 100`, AUTO returns `0.0`. |
| `is_auto` | `()` | `bool` | `True` if `type == UnitType.AUTO` |

### Factory Functions

| Function | Signature | Returns | Description |
|---|---|---|---|
| `px` | `(value: float)` | `Unit` | Create a pixel unit |
| `pct` | `(value: float)` | `Unit` | Create a percentage unit |

### Constant

| Name | Type | Description |
|---|---|---|
| `auto` | `Unit` | Pre-created `Unit(0, UnitType.AUTO)` |

### Usage

```python
from engine.ui.core.units import px, pct, auto

width = px(200)     # 200 pixels
height = pct(50)    # 50% of parent
size = auto         # computed by layout

# Resolve to pixels
pixels = pct(50).resolve(800)  # -> 400.0
```

---

## CSS Parser

**File**: `core/css_parser.py`
**Import**: `from engine.ui.core.css_parser import parse_css, parse_color, parse_length, parse_edge_shorthand`

### Function: `parse_css`

```python
parse_css(css_string: str) -> dict[str, str]
```

Parse a CSS declaration string into a dict of property name to raw value string.

```python
parse_css("width: 200px; padding: 10px 20px; background: #333")
# -> {"width": "200px", "padding": "10px 20px", "background": "#333"}
```

### Function: `parse_length`

```python
parse_length(value: str) -> tuple[float, str]
```

Parse a CSS length value. Returns `(number, unit_string)`.

| Input | Output |
|---|---|
| `"100px"` | `(100.0, "px")` |
| `"50%"` | `(50.0, "%")` |
| `"auto"` | `(0.0, "auto")` |
| `"none"` | `(0.0, "none")` |
| `"0"` | `(0.0, "px")` |

### Function: `parse_color`

```python
parse_color(value: str) -> Color | None
```

Parse a CSS color value. Returns `Color` or `None` if unparseable.

Supported formats:
- **Named colors**: `"red"`, `"blue"`, `"white"`, `"transparent"`, `"purple"`, `"pink"`, `"brown"`, `"navy"`, `"teal"`, `"gold"`, `"silver"`, `"gray"`, `"grey"`, `"darkgray"`, `"darkgrey"`, `"lightgray"`, `"lightgrey"`, `"black"`, `"green"`, `"lime"`, `"yellow"`, `"cyan"`, `"magenta"`, `"orange"`
- **Hex**: `"#rgb"`, `"#rrggbb"`, `"#rrggbbaa"`
- **Functional**: `"rgb(r, g, b)"`, `"rgba(r, g, b, a)"` where a is 0.0-1.0

### Function: `parse_edge_shorthand`

```python
parse_edge_shorthand(value: str) -> tuple[float, float, float, float]
```

Parse CSS shorthand for margin/padding. Returns `(top, right, bottom, left)`.

| Input | Output |
|---|---|
| `"10px"` | `(10, 10, 10, 10)` |
| `"10px 20px"` | `(10, 20, 10, 20)` |
| `"10px 20px 30px"` | `(10, 20, 30, 20)` |
| `"10px 20px 30px 40px"` | `(10, 20, 30, 40)` |

---

## Dataclass: `EdgeInsets`

**File**: `core/style.py`
**Import**: `from engine.ui.core.style import EdgeInsets`

CSS box model edge values (top, right, bottom, left order).

```python
@dataclass
class EdgeInsets:
    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0
    left: float = 0.0
```

### Static Constructors

| Method | Signature | Returns | Description |
|---|---|---|---|
| `EdgeInsets.all` | `(value: float)` | `EdgeInsets` | All four edges equal |
| `EdgeInsets.symmetric` | `(vertical: float = 0, horizontal: float = 0)` | `EdgeInsets` | Symmetric top/bottom and left/right |

### Properties

| Property | Type | Description |
|---|---|---|
| `horizontal` | `float` | `left + right` |
| `vertical` | `float` | `top + bottom` |

---

## Class: `Style`

**File**: `core/style.py`
**Import**: `from engine.ui.core.style import Style`

CSS-like style object. Can be created from a CSS string, keyword arguments, or both.

### Constructor

```python
Style(css: str = "", **kwargs)
```

Three creation patterns:
1. CSS string: `Style("width: 200px; padding: 10px; background: #333")`
2. Keywords: `Style(width=px(200), padding=EdgeInsets.all(10))`
3. Both: `Style("display: flex; gap: 10px", direction="row")` -- CSS applied first, then kwargs override.

### All Properties

#### Sizing

| Property | Type | Default | CSS Property |
|---|---|---|---|
| `width` | `Unit` | `auto` | `width` |
| `height` | `Unit` | `auto` | `height` |
| `min_width` | `float` | `0.0` | `min-width` |
| `min_height` | `float` | `0.0` | `min-height` |
| `max_width` | `float` | `inf` | `max-width` (`"none"` = inf) |
| `max_height` | `float` | `inf` | `max-height` (`"none"` = inf) |

#### Box Model

| Property | Type | Default | CSS Property |
|---|---|---|---|
| `padding` | `EdgeInsets` | `EdgeInsets()` | `padding`, `padding-top`, `padding-right`, `padding-bottom`, `padding-left` |
| `margin` | `EdgeInsets` | `EdgeInsets()` | `margin`, `margin-top`, `margin-right`, `margin-bottom`, `margin-left` |

#### Border

| Property | Type | Default | CSS Property |
|---|---|---|---|
| `border_width` | `float` | `0.0` | `border-width`, `border` shorthand |
| `border_color` | `Color \| None` | `None` | `border-color`, `border` shorthand |
| `border_radius` | `float` | `0.0` | `border-radius` |

#### Background

| Property | Type | Default | CSS Property |
|---|---|---|---|
| `background_color` | `Color \| None` | `None` | `background`, `background-color` |
| `background` | `Color \| None` | `None` | Alias for `background_color` (both set together) |
| `opacity` | `float` | `1.0` | `opacity` |

#### Layout (Flexbox)

| Property | Type | Default | CSS Property |
|---|---|---|---|
| `display` | `str` | `"flex"` | `display` |
| `direction` | `str` | `"column"` | `flex-direction` |
| `justify_content` | `str` | `"start"` | `justify-content` (values: `"start"`, `"end"`, `"center"`, `"space-between"`, `"space-around"`, `"space-evenly"`) |
| `align_items` | `str` | `"start"` | `align-items` (values: `"start"`, `"end"`, `"center"`, `"stretch"`) |
| `gap` | `float` | `0.0` | `gap` |
| `wrap` | `bool` | `False` | `flex-wrap` (`"wrap"` -> True) |

#### Flex Item

| Property | Type | Default | CSS Property |
|---|---|---|---|
| `flex_grow` | `float` | `0.0` | `flex-grow` |
| `flex_shrink` | `float` | `1.0` | `flex-shrink` |

#### Positioning

| Property | Type | Default | CSS Property |
|---|---|---|---|
| `position` | `str` | `"static"` | `position` (`"static"` or `"absolute"`) |
| `top` | `float \| None` | `None` | `top` |
| `right_pos` | `float \| None` | `None` | `right` |
| `bottom` | `float \| None` | `None` | `bottom` |
| `left_pos` | `float \| None` | `None` | `left` |

#### Text

| Property | Type | Default | CSS Property |
|---|---|---|---|
| `font` | `str \| None` | `None` | `font-family`, `font` |
| `font_size` | `int` | `16` | `font-size` |
| `color` | `Color \| None` | `None` | `color` |
| `text_align` | `str` | `"left"` | `text-align` |

### CSS Property Inheritance

The following properties are inherited from parent Style (via `resolve_inherited`):
- `color`
- `font`
- `font_size`
- `text_align`

Inheritance only fills `None` values from the parent.

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `copy` | `()` | `Style` | Shallow copy of the style |
| `resolve_inherited` | `(parent: Style \| None)` | `None` | Inherit `None`-valued properties from parent |

### Supported CSS Border Shorthand

`border: 1px solid #fff` -- extracts width and color, ignores style keyword (solid, dashed, etc.).

---

## Class: `Stylesheet`

**File**: `core/stylesheet.py`
**Import**: `from engine.ui.core.stylesheet import Stylesheet`

Collection of named CSS rules, like a CSS stylesheet. Supports `.class` and `#id` selectors.

### Constructor

```python
Stylesheet()
```

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add` | `(selector: str, css: str)` | `Stylesheet` | Add a CSS rule. Returns self for chaining. |
| `remove` | `(selector: str)` | `None` | Remove a rule by selector |
| `get` | `(selector: str)` | `str \| None` | Get CSS string for a selector |
| `apply` | `(element: Element)` | `None` | Apply matching rules to a single element's style. Matches `.class_name` and `#id`. |
| `apply_tree` | `(root: Element)` | `None` | Apply matching rules to entire element tree (depth-first) |

### Selector Matching

- `.class_name`: Matches elements whose `class_name` contains the class (space-separated).
- `#id`: Matches elements whose `id` equals the selector (without `#`).

If an element has multiple classes (e.g. `class_name="panel dark"`), rules for `.panel` and `.dark` both apply.

### Usage

```python
sheet = Stylesheet()
sheet.add(".panel", "background: rgba(0,0,0,0.8); padding: 10px; border-radius: 8px")
sheet.add(".title", "font-size: 24px; color: white; text-align: center")
sheet.add("#score", "font-size: 18px; color: gold")

panel = Div(class_name="panel")
sheet.apply(panel)       # apply to one element
sheet.apply_tree(root)   # apply to entire tree
```

---

## Class: `Element`

**File**: `core/element.py`
**Import**: `from engine.ui.core.element import Element`

Base UI element. DOM Node equivalent. Maintains a tree of children, handles event bubbling, and provides layout/render interface.

### Constructor

```python
Element(
    style: Style | str | None = None,
    id: str = "",
    class_name: str = "",
)
```

| Parameter | Type | Description |
|---|---|---|
| `style` | `Style \| str \| None` | A `Style` object, a CSS string (auto-wrapped in `Style(css)`), or `None` (empty style). |
| `id` | `str` | Element ID for selector matching and `find_by_id` |
| `class_name` | `str` | Space-separated CSS class names |

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `id` | `str` | yes | Element ID |
| `class_name` | `str` | yes | Space-separated class names |
| `style` | `Style` | yes | The element's style |
| `parent` | `Element \| None` | no | Parent element |
| `children` | `list[Element]` | no | Copy of children list |
| `computed_rect` | `Rect` | no | Layout-computed rect (local to parent content area) |
| `absolute_rect` | `Rect` | no | Rect in screen space (accumulated from all parents + padding + border) |
| `hovered` | `bool` | no | `True` if mouse is over this element |
| `focused` | `bool` | no | `True` if this element has focus |
| `visible` | `bool` | yes | If `False`, element and children are not drawn or hit-tested |

### Tree Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `append` | `(child: Element)` | `Element` | Add child at end. Returns the child. Removes from previous parent if any. |
| `prepend` | `(child: Element)` | `Element` | Add child at beginning. Returns the child. |
| `remove` | `(child: Element)` | `None` | Remove a child element |
| `remove_all` | `()` | `None` | Remove all children |

### Query Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `find_by_id` | `(id: str)` | `Element \| None` | Find descendant by ID (depth-first search) |
| `find_all_by_type` | `(elem_type: type)` | `list[Element]` | Find all descendants of a given type (including self) |

### Event Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `on` | `(event_name: str, handler: Callable[[UIEvent], None])` | `None` | Subscribe to an event (e.g. `"click"`, `"hover"`, `"focus"`) |
| `off` | `(event_name: str, handler: Callable \| None = None)` | `None` | Unsubscribe. If `handler` is `None`, removes all handlers for that event. |
| `emit` | `(event_name: str, event: UIEvent)` | `None` | Emit an event with bubbling (child -> parent). Stops if `event.stop_propagation()` is called. |

### Hit Test

| Method | Signature | Returns | Description |
|---|---|---|---|
| `hit_test` | `(x: float, y: float)` | `Element \| None` | Find the deepest visible element at screen position `(x, y)`. Children tested in reverse order (last = topmost = checked first). |

### Render Methods (override in subclasses)

| Method | Signature | Description |
|---|---|---|
| `draw` | `(renderer: Renderer, offset_x: float = 0, offset_y: float = 0)` | Draw self and children. Skips if not visible or `display == "none"`. |
| `_draw_self` | `(renderer: Renderer, ox: float, oy: float)` | Override to draw element-specific visuals (background, border, content). |
| `_draw_children` | `(renderer: Renderer, ox: float, oy: float)` | Draw all children with accumulated offset (position + padding + border). |

---

## Layout Engine

**File**: `core/layout.py`
**Import**: `from engine.ui.core.layout import compute_layout`

### Function: `compute_layout`

```python
compute_layout(root: Element, available_w: float, available_h: float) -> None
```

Compute flexbox layout for the entire element tree. Sets `_computed_x`, `_computed_y`, `_computed_w`, `_computed_h` on every `Element`.

| Parameter | Type | Description |
|---|---|---|
| `root` | `Element` | Root of the UI tree |
| `available_w` | `float` | Available width (typically viewport width) |
| `available_h` | `float` | Available height (typically viewport height) |

### Flexbox Algorithm

1. **Resolve sizes**: Width/height from `style.width`/`style.height` units. Auto width = parent width minus margins. Auto height = 0 (expanded by content later).
2. **Separate absolute children**: Absolutely-positioned children laid out independently.
3. **Calculate main-axis total**: Sum of child sizes + margins + gaps.
4. **Flex grow/shrink**: Distribute remaining space (or shrink overflow) proportionally by `flex_grow`/`flex_shrink`.
5. **Justify content**: Position children along main axis: `start`, `end`, `center`, `space-between`, `space-around`, `space-evenly`.
6. **Align items**: Position children along cross axis: `start`, `end`, `center`, `stretch`.
7. **Auto height**: If parent `height` is auto, expand to fit content.
8. **Recurse**: Layout grandchildren.

### Absolute Positioning

Elements with `style.position == "absolute"` are positioned relative to the parent's content area using `top`, `right`, `bottom`, `left` offsets.

---

## UI Events

**File**: `events.py`
**Import**: `from engine.ui.events import UIEvent, ClickEvent, HoverEvent, HoverExitEvent, FocusEvent, BlurEvent, ScrollEvent`

### Dataclass: `UIEvent`

Base UI event with bubbling support.

```python
@dataclass
class UIEvent:
    target: Element | None = None
    current_target: Element | None = None
    _stopped: bool = False
```

| Field | Type | Description |
|---|---|---|
| `target` | `Element \| None` | Element that originally triggered the event |
| `current_target` | `Element \| None` | Element currently handling the event (changes during bubbling) |

| Method | Signature | Description |
|---|---|---|
| `stop_propagation` | `()` | Stop event from bubbling to parent elements |

| Property | Type | Description |
|---|---|---|
| `propagation_stopped` | `bool` | `True` if `stop_propagation()` was called |

### Dataclass: `ClickEvent`

```python
@dataclass
class ClickEvent(UIEvent):
    x: float = 0.0
    y: float = 0.0
    button: int = 1  # 1=left, 2=middle, 3=right
```

### Dataclass: `HoverEvent`

```python
@dataclass
class HoverEvent(UIEvent):
    x: float = 0.0
    y: float = 0.0
```

### Dataclass: `HoverExitEvent`

```python
@dataclass
class HoverExitEvent(UIEvent):
    pass
```

### Dataclass: `FocusEvent`

```python
@dataclass
class FocusEvent(UIEvent):
    pass
```

### Dataclass: `BlurEvent`

```python
@dataclass
class BlurEvent(UIEvent):
    pass
```

### Dataclass: `ScrollEvent`

```python
@dataclass
class ScrollEvent(UIEvent):
    delta: float = 0.0
```

### Event Bubbling

When `element.emit("click", event)` is called:
1. Handlers on the current element fire.
2. If `stop_propagation()` was not called, the event bubbles to `parent.emit(...)`.
3. This continues up the tree until the root or propagation is stopped.

---

## Element: `Div`

**File**: `elements/div.py`
**Import**: `from engine.ui.elements.div import Div`
**Inherits**: `Element`

Container element. Like HTML `<div>`. Draws background, border, and border-radius.

### Constructor

```python
Div(style: Style | str | None = None, **kwargs)
```

`**kwargs` passed to `Element.__init__` (supports `id`, `class_name`).

### Usage

```python
panel = Div(style="width: 300px; height: 200px; background: rgba(40,40,40,0.8); "
                  "border: 1px solid white; border-radius: 8px; "
                  "padding: 10px; display: flex; flex-direction: column; gap: 5px")

# With children
container = Div(style="display: flex; gap: 10px")
container.append(Text("Hello"))
container.append(Text("World"))
```

---

## Element: `Text`

**File**: `elements/text.py`
**Import**: `from engine.ui.elements.text import Text` (exported as `UIText` from engine)
**Inherits**: `Element`

Text display element. Like HTML `<span>` or text node. Renders text using SDL_ttf.

### Constructor

```python
Text(content: str = "", style: Style | str | None = None, **kwargs)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `content` | `str` | yes | Text content. Setting marks for rebuild and triggers layout invalidation. |

### Behavior

- Rebuilds the SDL texture when `content` changes or on first draw.
- If `style.width` is auto, `_computed_w` is set to text width + padding.
- If `style.height` is auto, `_computed_h` is set to text height + padding.
- Respects `style.text_align` (`"left"`, `"center"`, `"right"`) within available width.
- Requires `style.font` to be set (TTF font path). No text renders without a font.
- Renders at draw layer `1001` (above `Div` backgrounds at layer `1000`).

### Usage

```python
Text("Score: 0", style="font: 'fonts/mono.ttf'; font-size: 18px; color: white")
Text("HP: 100", style="color: red; font-size: 24px", class_name="hud-text")
```

---

## Element: `Image`

**File**: `elements/image.py`
**Import**: `from engine.ui.elements.image import Image` (exported as `UIImage` from engine)
**Inherits**: `Element`

Image display element. Like HTML `<img>`. Draws a background box, then renders the image inside.

### Constructor

```python
Image(src: str = "", style: Style | str | None = None, **kwargs)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `src` | `str` | yes | Image file path. Setting clears cached texture. |

### Behavior

- Loads image via `ResourceManager` on first draw.
- Image fills the content area (computed size minus padding and border).
- Renders at draw layer `1001`.

### Usage

```python
Image("icons/heart.png", style="width: 32px; height: 32px")
```

---

## Element: `Button`

**File**: `elements/button.py`
**Import**: `from engine.ui.elements.button import Button`
**Inherits**: `Element`

Clickable button with a text label. Has hover and active visual states.

### Constructor

```python
Button(label: str = "", style: Style | str | None = None, **kwargs)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `label` | `str` | yes | Button text. Setting updates the internal `Text` element. |
| `hover_color` | `Color \| None` | yes | Background color when hovered. `None` = auto-lighten by +20. |
| `active_color` | `Color \| None` | yes | Background color when pressed. `None` = auto-darken by -30. |

### Behavior

- Contains an internal `Text` element for the label.
- Inherits `font`, `font_size`, `color` from the button's style to the label.
- Label is centered horizontally (`text_align: center`) and vertically.
- Background color changes on hover (lighter) and press (darker).
- Use `button.on("click", handler)` to handle clicks.

### Usage

```python
btn = Button("Start Game", style="width: 200px; height: 50px; "
             "background: #3c3c3c; border-radius: 6px; "
             "font: 'fonts/ui.ttf'; font-size: 18px; color: white")
btn.on("click", lambda e: print("Clicked!"))
```

---

## Element: `ProgressBar`

**File**: `elements/progress_bar.py`
**Import**: `from engine.ui.elements.progress_bar import ProgressBar`
**Inherits**: `Element`

A progress/health bar element with configurable fill and auto-color based on value thresholds.

### Constructor

```python
ProgressBar(value: float = 1.0, style: Style | str | None = None, **kwargs)
```

### Properties

| Property | Type | Writable | Default | Description |
|---|---|---|---|---|
| `value` | `float` | yes | `1.0` | Progress value, clamped to 0.0--1.0 |
| `fill_color` | `Color` | yes | `Color.GREEN` | Fill color when value >= mid_threshold |
| `low_color` | `Color` | yes | `Color.RED` | Fill color when value < low_threshold |
| `mid_color` | `Color` | yes | `Color.YELLOW` | Fill color when value < mid_threshold |
| `low_threshold` | `float` | yes | `0.25` | Threshold below which `low_color` is used |
| `mid_threshold` | `float` | yes | `0.5` | Threshold below which `mid_color` is used |
| `auto_color` | `bool` | yes | `True` | If `True`, fill color changes automatically based on value and thresholds. If `False`, always uses `fill_color`. |

### Behavior

- Background is drawn from `style.background_color`.
- Fill bar is drawn inside the border, width proportional to `value`.
- Fill bar respects `border_radius` (adjusted for border width).
- Fill renders at layer `1001`.

### Usage

```python
bar = ProgressBar(0.75, style="width: 200px; height: 20px; "
                  "background: #333; border-radius: 4px")
bar.fill_color = Color.GREEN
bar.value = 0.5  # updates fill width

# Auto-color: red below 25%, yellow below 50%, green above
bar.auto_color = True
bar.value = 0.1  # fill is red
```

---

## Class: `UIRoot`

**File**: `ui_root.py`
**Import**: `from engine.ui.ui_root import UIRoot`
**Inherits**: `Component`

Component that owns a UI element tree and drives layout, rendering, and input events. Attach to an Entity to create a UI layer.

### Constructor

```python
UIRoot(width: int = 800, height: int = 600)
```

| Parameter | Type | Description |
|---|---|---|
| `width` | `int` | Layout viewport width (typically window width) |
| `height` | `int` | Layout viewport height (typically window height) |

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `root` | `Element` | no | The root element of the UI tree. Append children here. |
| `focused` | `Element \| None` | no | Currently focused element |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `set_focus` | `(element: Element \| None)` | `None` | Set focus. Emits `"blur"` on old and `"focus"` on new element. |
| `invalidate` | `()` | `None` | Force layout recalculation on next frame |

### Lifecycle Hooks Used

- `on_update(dt)`: Performs hit testing against mouse position. Emits `"hover"`, `"hover_exit"`, and `"click"` events. Sets hover/focus state on elements.
- `on_draw(renderer)`: Recomputes layout if dirty, then draws the entire UI tree in screen space (no camera transform).

### Event Handling

Each frame in `on_update`:
1. Hit-test mouse position against the element tree.
2. If the hovered element changed, emit `"hover_exit"` on the old element and `"hover"` on the new one.
3. On left-click (`MouseButton.LEFT`), emit `"click"` with `ClickEvent(x, y, button=1)` on the hit element and set focus.
4. On right-click (`MouseButton.RIGHT`), emit `"click"` with `ClickEvent(x, y, button=3)` on the hit element.

### Usage

```python
ui_entity = Entity("HUD")
ui = ui_entity.add_component(UIRoot(800, 600))

panel = Div(style="width: 200px; padding: 10px; "
            "background: rgba(0,0,0,180); border-radius: 8px")
panel.append(Text("HP: 100", style="font: 'fonts/ui.ttf'; font-size: 16px; color: red"))

hp_bar = ProgressBar(1.0, style="width: 180px; height: 16px; "
                     "background: #333; border-radius: 4px")
panel.append(hp_bar)

ui.root.append(panel)
scene.add(ui_entity)

# Update HP bar from game logic
hp_bar.value = player_hp / max_hp
```

---

## Full UI Example

```python
from engine import (
    Game, Scene, Entity, Vector2, Color,
    px, pct, auto, Style, EdgeInsets,
    Div, UIText, Button, ProgressBar, UIRoot,
)

class HUDScene(Scene):
    def on_enter(self):
        # UI entity
        ui_entity = Entity("UI")
        ui = ui_entity.add_component(UIRoot(800, 600))

        # Main container
        hud = Div(style="width: 100%; height: 100%; padding: 10px; "
                  "display: flex; flex-direction: column; gap: 10px")

        # Top bar
        top = Div(style="display: flex; flex-direction: row; gap: 10px; "
                  "align-items: center")
        top.append(UIText("HP:", style="font: 'fonts/ui.ttf'; font-size: 16px; color: white"))
        top.append(ProgressBar(0.8, style="width: 200px; height: 20px; "
                              "background: #333; border-radius: 4px"))
        hud.append(top)

        # Button
        btn = Button("Menu", style="width: 100px; height: 40px; "
                    "background: #444; border-radius: 6px; "
                    "font: 'fonts/ui.ttf'; font-size: 14px; color: white")
        btn.on("click", lambda e: print("Menu clicked"))
        hud.append(btn)

        ui.root.append(hud)
        self.add(ui_entity)

game = Game(title="UI Demo", width=800, height=600)
game.run(HUDScene())
```
