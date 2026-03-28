# engine.input — API Reference

## Enum: `Key`

**File**: `keys.py`
**Import**: `from engine.input import Key`
**Base**: `IntEnum`

SDL2 keycode constants. Values map directly to `SDLK_*` constants.

### Members

| Group | Members |
|---|---|
| Letters | `A` through `Z` |
| Numbers | `NUM_0` through `NUM_9` |
| Arrows | `UP`, `DOWN`, `LEFT`, `RIGHT` |
| Special | `SPACE`, `RETURN`, `ESCAPE`, `TAB`, `BACKSPACE`, `DELETE` |
| Modifiers | `LSHIFT`, `RSHIFT`, `LCTRL`, `RCTRL`, `LALT`, `RALT` |
| Function | `F1` through `F12` |

---

## Enum: `MouseButton`

**File**: `keys.py`
**Import**: `from engine.input import MouseButton`
**Base**: `IntEnum`

| Member | Value | Description |
|---|---|---|
| `LEFT` | `SDL_BUTTON_LEFT` | Left mouse button |
| `MIDDLE` | `SDL_BUTTON_MIDDLE` | Middle mouse button |
| `RIGHT` | `SDL_BUTTON_RIGHT` | Right mouse button |

---

## Class: `Keyboard`

**File**: `keyboard.py`
**Import**: `from engine.input import Keyboard`

Double-buffered keyboard state. Tracks current and previous frame to distinguish pressed/just_pressed/just_released.

### Constructor

```python
Keyboard()
```

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `update` | `()` | `None` | Swap buffers (previous ← current). Called by `App.poll_events()` before processing events. |
| `process_event` | `(event: SDL_Event)` | `None` | Process a single SDL event. Called by `App.poll_events()`. |
| `is_pressed` | `(key: Key)` | `bool` | `True` while the key is held down |
| `is_just_pressed` | `(key: Key)` | `bool` | `True` only on the frame the key was pressed |
| `is_just_released` | `(key: Key)` | `bool` | `True` only on the frame the key was released |

### Frame Lifecycle

```
App.poll_events()
  → keyboard.update()        # swap previous ← current
  → for each SDL event:
      keyboard.process_event(event)  # update current state
```

After `poll_events()`, query methods reflect the new frame's state.

---

## Class: `Mouse`

**File**: `mouse.py`
**Import**: `from engine.input import Mouse`

Double-buffered mouse state. Tracks position, buttons, scroll.

### Constructor

```python
Mouse()
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `position` | `Vector2` | no | Current mouse position in screen pixels |
| `scroll_delta` | `float` | no | Scroll wheel delta this frame (positive = up) |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `update` | `()` | `None` | Swap buffers, reset scroll delta. Called by `App.poll_events()`. |
| `process_event` | `(event: SDL_Event)` | `None` | Process a single SDL event. Called by `App.poll_events()`. |
| `is_pressed` | `(button: MouseButton)` | `bool` | `True` while button is held |
| `is_just_pressed` | `(button: MouseButton)` | `bool` | `True` only on frame button was pressed |
| `is_just_released` | `(button: MouseButton)` | `bool` | `True` only on frame button was released |
