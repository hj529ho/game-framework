# engine.tween -- API Reference

## Enum: `LoopType`

**File**: `tween.py`
**Import**: `from engine.tween.tween import LoopType`
**Base**: `Enum`

| Member | Description |
|---|---|
| `LoopType.NONE` | Play once and stop |
| `LoopType.RESTART` | Restart from beginning each loop |
| `LoopType.YOYO` | Ping-pong back and forth (reverse direction each loop) |

---

## Class: `Tween`

**File**: `tween.py`
**Import**: `from engine.tween.tween import Tween`

A single property animation. DOTween-style API. Tweens a value from start to end over a duration using an easing function. Supports chaining for configuration.

### Constructor

```python
Tween(
    getter: Callable[[], Any],
    setter: Callable[[Any], None],
    start_val: Any,
    end_val: Any,
    duration: float,
)
```

| Parameter | Type | Description |
|---|---|---|
| `getter` | `Callable[[], Any]` | Function returning the current value |
| `setter` | `Callable[[Any], None]` | Function to set the new value |
| `start_val` | `Any` | Start value. Supports `float`, `int`, `Vector2`, `Color`. |
| `end_val` | `Any` | End value (same type as start) |
| `duration` | `float` | Duration in seconds (minimum 0.001) |

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `is_alive` | `bool` | no | `True` while the tween is active |
| `is_paused` | `bool` | no | `True` while the tween is paused |

### Chaining API (returns `self` for method chaining)

| Method | Signature | Returns | Description |
|---|---|---|---|
| `set_ease` | `(ease: str \| Callable[[float], float])` | `Tween` | Set easing function. String names from `EASINGS` dict or a custom `(float) -> float`. Default: `linear`. |
| `set_delay` | `(delay: float)` | `Tween` | Set delay before tween starts (seconds) |
| `set_loops` | `(count: int = -1, loop_type: LoopType = LoopType.RESTART)` | `Tween` | Set looping. `count=-1` = infinite, `0` = no loop, `N` = N extra loops. |
| `on_complete` | `(callback: Callable[[], None])` | `Tween` | Callback when tween finishes |
| `on_update` | `(callback: Callable[[float], None])` | `Tween` | Callback each frame with progress (0.0 to 1.0) |
| `on_start` | `(callback: Callable[[], None])` | `Tween` | Callback when tween first starts (after delay) |

### Control Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `play` | `()` | `Tween` | Add this tween to the global `TweenManager` and start it. Returns self. |
| `pause` | `()` | `None` | Pause the tween |
| `resume` | `()` | `None` | Resume a paused tween |
| `kill` | `()` | `None` | Stop the tween immediately (no callback) |
| `complete` | `()` | `None` | Jump to end immediately, apply final value, fire `on_complete` callback |

### Factory Methods (static)

All factory methods return an unstarted `Tween`. Call `.play()` to start.

| Method | Signature | Returns | Description |
|---|---|---|---|
| `Tween.to` | `(getter: Callable[[], Any], setter: Callable[[Any], None], end_val: Any, duration: float)` | `Tween` | Tween from current value (called at creation time) to `end_val` |
| `Tween.from_to` | `(setter: Callable[[Any], None], start_val: Any, end_val: Any, duration: float)` | `Tween` | Tween from explicit `start_val` to `end_val` |
| `Tween.move` | `(entity, target: Vector2, duration: float)` | `Tween` | Tween entity position to target |
| `Tween.scale_to` | `(entity, target: Vector2, duration: float)` | `Tween` | Tween entity scale to target |
| `Tween.rotate_to` | `(entity, target: float, duration: float)` | `Tween` | Tween entity rotation to target degrees |
| `Tween.fade` | `(component, target_alpha: float, duration: float)` | `Tween` | Tween a component's `opacity` or `alpha` field to target |

### Supported Interpolation Types

The internal `_interpolate` function handles:
- `float` / `int`: linear interpolation
- `Vector2`: `start.lerp(end, t)`
- `Color`: `start.lerp(end, t)`
- Other types: snaps to `end` at t >= 1.0

### Usage

```python
# Move entity with easing
Tween.move(entity, Vector2(400, 300), 1.0).set_ease("ease_out_back").play()

# Fade out over 0.5s with callback
Tween.fade(sprite, 0.0, 0.5).on_complete(lambda: entity.active = False).play()

# Generic tween with delay and looping
Tween.to(
    lambda: obj.value,
    lambda v: setattr(obj, 'value', v),
    100.0, 2.0,
).set_delay(0.5).set_loops(-1, LoopType.YOYO).set_ease("ease_in_out_sine").play()
```

---

## Class: `TweenSequence`

**File**: `tween.py`
**Import**: `from engine.tween.tween import TweenSequence`

Play tweens one after another in sequence.

### Constructor

```python
TweenSequence()
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `is_alive` | `bool` | no | `True` while the sequence is active |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `append` | `(tween: Tween)` | `TweenSequence` | Add a tween to the end of the sequence. Returns self. |
| `append_interval` | `(seconds: float)` | `TweenSequence` | Add a wait interval. Returns self. |
| `on_complete` | `(callback: Callable[[], None])` | `TweenSequence` | Callback when entire sequence finishes. Returns self. |
| `play` | `()` | `TweenSequence` | Add to global TweenManager and start. Returns self. |
| `kill` | `()` | `None` | Stop the sequence immediately |

### Usage

```python
seq = TweenSequence()
seq.append(Tween.move(entity, Vector2(100, 100), 0.5))
seq.append(Tween.move(entity, Vector2(400, 100), 0.5))
seq.append_interval(0.3)
seq.append(Tween.move(entity, Vector2(400, 400), 0.5))
seq.on_complete(lambda: print("Done!"))
seq.play()
```

---

## Class: `TweenParallel`

**File**: `tween.py`
**Import**: `from engine.tween.tween import TweenParallel`

Play multiple tweens simultaneously. Completes when all tweens finish.

### Constructor

```python
TweenParallel()
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `is_alive` | `bool` | no | `True` while any tween is still alive |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add` | `(tween: Tween)` | `TweenParallel` | Add a tween to run in parallel. Returns self. |
| `on_complete` | `(callback: Callable[[], None])` | `TweenParallel` | Callback when all tweens finish. Returns self. |
| `play` | `()` | `TweenParallel` | Add to global TweenManager and start. Returns self. |
| `kill` | `()` | `None` | Stop all tweens immediately |

### Usage

```python
par = TweenParallel()
par.add(Tween.move(entity, Vector2(400, 300), 1.0))
par.add(Tween.rotate_to(entity, 360, 1.0))
par.on_complete(lambda: print("All done!"))
par.play()
```

---

## Class: `TweenManager`

**File**: `tween.py`
**Import**: `from engine.tween.tween import TweenManager`
**Inherits**: `Component`

Component that drives all tweens. Must exist in the scene for `Tween.play()` to work. The first `TweenManager` to awake becomes the global manager.

### Constructor

```python
TweenManager()
```

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add` | `(tween: Tween)` | `None` | Add a tween to be updated |
| `add_sequence` | `(seq: TweenSequence)` | `None` | Add a sequence to be updated |
| `add_parallel` | `(par: TweenParallel)` | `None` | Add a parallel group to be updated |
| `kill_all` | `()` | `None` | Kill all active tweens, sequences, and parallels |

### Lifecycle Hooks Used

- `on_awake()`: Registers self as the global tween manager (if none exists).
- `on_update(dt)`: Updates all active tweens, sequences, and parallels. Removes completed ones.

### Required Setup

```python
# Add to your scene to enable Tween.play()
mgr = Entity("TweenManager")
mgr.add_component(TweenManager())
scene.add(mgr)

# Now Tween.play() works
Tween.move(entity, Vector2(100, 200), 1.0).play()
```

If no `TweenManager` exists when `Tween.play()` is called, a `RuntimeError` is raised.
