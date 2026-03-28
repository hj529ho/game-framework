# engine.input -- API Reference

## Enum: `Key`

**File**: `keys.py`
**Import**: `from engine.input.keys import Key`
**Base**: `IntEnum`

SDL2 keycode constants. Values map directly to `SDLK_*` constants.

### Members

| Group | Members |
|---|---|
| Letters | `A`, `B`, `C`, `D`, `E`, `F`, `G`, `H`, `I`, `J`, `K`, `L`, `M`, `N`, `O`, `P`, `Q`, `R`, `S`, `T`, `U`, `V`, `W`, `X`, `Y`, `Z` |
| Numbers | `NUM_0`, `NUM_1`, `NUM_2`, `NUM_3`, `NUM_4`, `NUM_5`, `NUM_6`, `NUM_7`, `NUM_8`, `NUM_9` |
| Arrows | `UP`, `DOWN`, `LEFT`, `RIGHT` |
| Special | `SPACE`, `RETURN`, `ESCAPE`, `TAB`, `BACKSPACE`, `DELETE` |
| Modifiers | `LSHIFT`, `RSHIFT`, `LCTRL`, `RCTRL`, `LALT`, `RALT` |
| Function keys | `F1`, `F2`, `F3`, `F4`, `F5`, `F6`, `F7`, `F8`, `F9`, `F10`, `F11`, `F12` |

---

## Enum: `MouseButton`

**File**: `keys.py`
**Import**: `from engine.input.keys import MouseButton`
**Base**: `IntEnum`

| Member | SDL2 Constant | Description |
|---|---|---|
| `LEFT` | `SDL_BUTTON_LEFT` | Left mouse button |
| `MIDDLE` | `SDL_BUTTON_MIDDLE` | Middle mouse button |
| `RIGHT` | `SDL_BUTTON_RIGHT` | Right mouse button |

---

## Class: `Keyboard`

**File**: `keyboard.py`
**Import**: `from engine.input.keyboard import Keyboard`

Double-buffered keyboard state. Tracks current and previous frame to distinguish pressed/just_pressed/just_released.

Created internally by `App`. Access via `current_app().keyboard`.

### Constructor

```python
Keyboard()
```

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `update` | `() -> None` | `None` | Swap buffers (previous = current.copy()). Called by `App.poll_events()` before processing events. |
| `process_event` | `(event: SDL_Event) -> None` | `None` | Process a single SDL key event. Called by `App.poll_events()`. |
| `is_pressed` | `(key: Key) -> bool` | `bool` | True while the key is held down |
| `is_just_pressed` | `(key: Key) -> bool` | `bool` | True only on the frame the key went from up to down |
| `is_just_released` | `(key: Key) -> bool` | `bool` | True only on the frame the key went from down to up |

### Frame Lifecycle

```
App.poll_events():
  keyboard.update()              -- swap previous = current
  for each SDL event:
    keyboard.process_event(event)  -- update current set
```

After `poll_events()`, query methods reflect the new frame's state.

### Usage

```python
kb = current_app().keyboard
if kb.is_just_pressed(Key.SPACE):
    jump()
if kb.is_pressed(Key.A):
    move_left()
```

---

## Class: `Mouse`

**File**: `mouse.py`
**Import**: `from engine.input.mouse import Mouse`

Double-buffered mouse state. Tracks position, button presses, and scroll wheel.

Created internally by `App`. Access via `current_app().mouse`.

### Constructor

```python
Mouse()
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `position` | `Vector2` | no | Current mouse position in screen pixels |
| `scroll_delta` | `float` | no | Scroll wheel delta this frame (positive = scroll up). Reset each frame. |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `update` | `() -> None` | `None` | Swap buffers, reset `scroll_delta` to 0. Called by `App.poll_events()`. |
| `process_event` | `(event: SDL_Event) -> None` | `None` | Process a single SDL mouse event. Called by `App.poll_events()`. |
| `is_pressed` | `(button: MouseButton) -> bool` | `bool` | True while button is held down |
| `is_just_pressed` | `(button: MouseButton) -> bool` | `bool` | True only on the frame the button went down |
| `is_just_released` | `(button: MouseButton) -> bool` | `bool` | True only on the frame the button went up |

### Usage

```python
mouse = current_app().mouse
if mouse.is_just_pressed(MouseButton.LEFT):
    print(f"Clicked at {mouse.position}")
scroll = mouse.scroll_delta  # e.g. +1.0 or -1.0
```
