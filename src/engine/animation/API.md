# engine.animation -- API Reference

## Dataclass: `FrameEvent`

**File**: `clip.py`
**Import**: `from engine.animation.clip import FrameEvent`

Callback triggered when a specific frame is reached during animation playback.

```python
@dataclass
class FrameEvent:
    frame: int
    callback: Callable[[], None]
```

| Field | Type | Description |
|---|---|---|
| `frame` | `int` | Frame index (into the clip's `frames` list) that triggers the callback |
| `callback` | `Callable[[], None]` | Function to call when the frame is reached |

---

## Dataclass: `AnimationClip`

**File**: `clip.py`
**Import**: `from engine.animation.clip import AnimationClip`

A single animation definition: frame list, playback speed, looping, and per-frame events.

```python
@dataclass
class AnimationClip:
    name: str
    frames: list[int]
    fps: float = 10.0
    loop: bool = True
    events: list[FrameEvent] = field(default_factory=list)
```

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | (required) | Clip name identifier |
| `frames` | `list[int]` | (required) | Frame indices in the spritesheet grid |
| `fps` | `float` | `10.0` | Playback speed (frames per second) |
| `loop` | `bool` | `True` | Whether to loop when all frames have played |
| `events` | `list[FrameEvent]` | `[]` | Per-frame event callbacks |

### Properties

| Property | Type | Description |
|---|---|---|
| `frame_count` | `int` | `len(self.frames)` |
| `duration` | `float` | Total duration in seconds: `len(frames) / fps`. Returns 0 if fps <= 0. |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add_event` | `(frame: int, callback: Callable[[], None])` | `None` | Register a callback for a specific frame index |

### Usage

```python
clip = AnimationClip(
    name="attack",
    frames=[0, 1, 2, 3, 4],
    fps=12,
    loop=False,
)
clip.add_event(2, lambda: print("Slash!"))
clip.add_event(4, lambda: print("Done!"))
```

---

## Class: `AnimationState`

**File**: `state_machine.py`
**Import**: `from engine.animation.state_machine import AnimationState`

A single state in the state machine, wrapping an `AnimationClip`. Manages frame advancement, looping, and event firing.

### Constructor

```python
AnimationState(name: str, clip: AnimationClip)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `name` | `str` | yes | State name |
| `clip` | `AnimationClip` | yes | The animation clip for this state |
| `current_frame` | `int` | no | Current frame value from `clip.frames[frame_index]`. Returns 0 if no frames. |
| `frame_index` | `int` | no | Current index into the clip's frames list |
| `normalized_time` | `float` | no | 0.0 to 1.0 progress through the clip |
| `is_finished` | `bool` | no | `True` when a non-looping clip has reached the last frame |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `reset` | `()` | `None` | Reset to frame 0, clear timer and events fired set |
| `update` | `(dt: float)` | `None` | Advance time, update frame index, fire events, handle loop/finish |

---

## Dataclass: `AnimationTransition`

**File**: `state_machine.py`
**Import**: `from engine.animation.state_machine import AnimationTransition`

Defines a transition rule between two animation states.

```python
@dataclass
class AnimationTransition:
    from_state: str
    to_state: str
    condition: Callable[[dict[str, Any]], bool] | None = None
    exit_time: float | None = None
```

| Field | Type | Default | Description |
|---|---|---|---|
| `from_state` | `str` | (required) | Source state name. `"*"` matches any state. |
| `to_state` | `str` | (required) | Target state name |
| `condition` | `Callable[[dict[str, Any]], bool] \| None` | `None` | Callable that takes the parameter dict and returns `bool`. `None` = no condition (only exit_time). |
| `exit_time` | `float \| None` | `None` | Fraction of clip (0.0 to 1.0) that must play before transition triggers. `None` = check condition every frame. |

### Properties

| Property | Type | Description |
|---|---|---|
| `has_exit_time` | `bool` | `True` if `exit_time is not None` |

---

## Class: `AnimatorStateMachine`

**File**: `state_machine.py`
**Import**: `from engine.animation.state_machine import AnimatorStateMachine`

Unity-style animation state machine. Manages states (each wrapping an `AnimationClip`), transitions driven by parameters, and state callbacks.

### Constructor

```python
AnimatorStateMachine()
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `current_state` | `str` | no | Name of the current state. Empty string if none. |
| `current_frame` | `int` | no | Current frame value of the active state. 0 if none. |
| `is_finished` | `bool` | no | `True` if the current state's clip has finished (non-looping). `True` if no state. |
| `normalized_time` | `float` | no | 0.0 to 1.0 progress of the current state. 1.0 if no state. |

### State Management Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add_state` | `(name: str, clip: AnimationClip)` | `None` | Register a named state |
| `play` | `(name: str)` | `None` | Force-switch to a state, resetting it. Fires exit/enter callbacks. Raises `ValueError` if name not found. |

### Parameter Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `set_param` | `(name: str, value: Any)` | `None` | Set a parameter value |
| `get_param` | `(name: str)` | `Any` | Get a parameter value. Returns `None` if not set. |

### Transition Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add_transition` | `(from_state: str, to_state: str, condition: Callable[[dict[str, Any]], bool] \| None = None, exit_time: float \| None = None)` | `None` | Add a transition rule. `from_state="*"` matches any state. |

### Callback Methods

| Method | Signature | Description |
|---|---|---|
| `on_state_enter` | `(callback: Callable[[str, str], None])` | Register callback `(old_state, new_state)` called on state enter |
| `on_state_exit` | `(callback: Callable[[str], None])` | Register callback `(old_state)` called on state exit |

### Frame Method

| Method | Signature | Returns | Description |
|---|---|---|---|
| `update` | `(dt: float)` | `None` | Update current state and check transitions |

### Transition Evaluation Order

For each transition in registration order:
1. Check `from_state` matches current state (or is `"*"`).
2. Skip self-transitions unless `from_state == "*"`.
3. If `has_exit_time`, check that `normalized_time >= exit_time`.
4. If `condition` is set, check `condition(params)`.
5. First transition that passes all checks is taken.

### Usage

```python
asm = AnimatorStateMachine()
asm.add_state("idle", AnimationClip("idle", [0, 1, 2, 3], fps=8))
asm.add_state("run", AnimationClip("run", [4, 5, 6, 7, 8, 9], fps=12))
asm.add_state("attack", AnimationClip("attack", [10, 11, 12, 13], fps=15, loop=False))

asm.set_param("speed", 0.0)
asm.set_param("attacking", False)

asm.add_transition("idle", "run", condition=lambda p: p["speed"] > 0.1)
asm.add_transition("run", "idle", condition=lambda p: p["speed"] <= 0.1)
asm.add_transition("*", "attack", condition=lambda p: p["attacking"])
asm.add_transition("attack", "idle", exit_time=1.0)

asm.play("idle")
```

---

## Class: `Animator`

**File**: `animator.py`
**Import**: `from engine.animation.animator import Animator`
**Inherits**: `Component`

Component that combines `AnimatorStateMachine` with spritesheet rendering. Attach to an Entity to animate it.

### Constructor

```python
Animator(
    image: str = "",
    frame_width: int = 32,
    frame_height: int = 32,
    layer: int = 0,
)
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `state_machine` | `AnimatorStateMachine` | no | The underlying state machine |
| `current_state` | `str` | no | Delegates to `state_machine.current_state` |
| `current_frame` | `int` | no | Delegates to `state_machine.current_frame` |
| `image` | `str` | yes | Spritesheet image path. Setting clears cached texture. |
| `layer` | `int` | yes | Render layer |
| `anchor` | `Vector2` | yes | Anchor point. Default: `(0.5, 0.5)` (center). |
| `flip_x` | `bool` | yes | Horizontal flip. Default: `False`. |
| `flip_y` | `bool` | yes | Vertical flip. Default: `False`. |

### Delegated Methods (to state_machine)

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add_state` | `(name: str, clip: AnimationClip)` | `None` | Register an animation state |
| `add_transition` | `(from_state: str, to_state: str, condition: ... \| None = None, exit_time: float \| None = None)` | `None` | Add a transition rule |
| `set_param` | `(name: str, value: Any)` | `None` | Set a parameter |
| `get_param` | `(name: str)` | `Any` | Get a parameter |
| `play` | `(name: str)` | `None` | Force-switch to a state |

### Lifecycle Hooks Used

- `on_update(dt)`: Calls `state_machine.update(dt)` to advance animation and check transitions.
- `on_draw(renderer)`: Renders the current frame from the spritesheet, applying camera transform, entity scale, rotation, and flip flags.

### Usage

```python
animator = entity.add_component(Animator(
    image="player.png",
    frame_width=32,
    frame_height=32,
))

idle = AnimationClip("idle", [0, 1, 2, 3], fps=8)
run = AnimationClip("run", [4, 5, 6, 7, 8, 9], fps=12)
attack = AnimationClip("attack", [10, 11, 12, 13], fps=15, loop=False)
attack.add_event(2, lambda: print("Slash!"))

animator.add_state("idle", idle)
animator.add_state("run", run)
animator.add_state("attack", attack)

animator.add_transition("idle", "run", condition=lambda p: p["speed"] > 0.1)
animator.add_transition("run", "idle", condition=lambda p: p["speed"] <= 0.1)
animator.add_transition("*", "attack", condition=lambda p: p["attacking"])
animator.add_transition("attack", "idle", exit_time=1.0)

animator.play("idle")

# In update:
animator.set_param("speed", current_speed)
animator.set_param("attacking", attack_pressed)
```
