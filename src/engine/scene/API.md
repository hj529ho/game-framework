# engine.scene -- API Reference

## Class: `Scene`

**File**: `scene.py`
**Import**: `from engine.scene.scene import Scene`

Owns a `World` of entities. Subclass and override lifecycle hooks for custom scenes.

### Constructor

```python
Scene(name: str = "")  # defaults to class name if empty
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `name` | `str` | no | Scene name (defaults to class `__name__` if not provided) |
| `world` | `World` | no | The entity container for this scene |

### Entity Convenience Methods

All delegate to `self.world`:

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add` | `(entity: Entity)` | `Entity` | Add entity to this scene's world |
| `remove` | `(entity: Entity)` | `None` | Remove entity from this scene's world |
| `find` | `(name: str)` | `Entity \| None` | Find entity by name |
| `find_by_tag` | `(tag: str)` | `list[Entity]` | Find entities by tag |
| `find_with_component` | `(*comp_types: type[Component])` | `list[Entity]` | Find entities having all given component types |

### Lifecycle Hooks (override in subclass)

| Hook | Signature | When Called |
|---|---|---|
| `on_enter` | `() -> None` | Scene becomes active (pushed or replaces another) |
| `on_exit` | `() -> None` | Scene is removed from the stack (popped or replaced) |
| `on_pause` | `() -> None` | Another scene is pushed on top of this one |
| `on_resume` | `() -> None` | The scene above this one was popped |

### Frame Methods (called by SceneManager)

| Method | Signature | Description |
|---|---|---|
| `update` | `(dt: float) -> None` | Calls `self.world.update(dt)` |
| `draw` | `(renderer: Renderer) -> None` | Calls `self.world.draw(renderer)` |

### Usage

```python
class GameScene(Scene):
    def on_enter(self):
        player = Entity("Player")
        player.position = Vector2(400, 300)
        player.add_component(PlayerMovement())
        self.add(player)

    def on_exit(self):
        self.world.clear()
```

---

## Class: `SceneManager`

**File**: `scene_manager.py`
**Import**: `from engine.scene.scene_manager import SceneManager`

Stack-based scene manager with deferred transitions. Scene changes are queued and processed after the current frame.

### Constructor

```python
SceneManager()
```

### Properties

| Property | Type | Description |
|---|---|---|
| `current` | `Scene \| None` | Top of the stack, or `None` if empty |
| `stack_depth` | `int` | Number of scenes on the stack |
| `transitioning` | `bool` | `True` if a transition is currently running |

### Scene Management Methods

All operations are **deferred**. Pass an optional `Transition` for animated scene changes.

| Method | Signature | Description |
|---|---|---|
| `push` | `(scene: Scene, transition: Transition \| None = None) -> None` | Push a scene on top. Calls `current.on_pause()` then `scene.on_enter()`. |
| `pop` | `(transition: Transition \| None = None) -> None` | Pop the top scene. Calls `top.on_exit()` then `new_top.on_resume()`. |
| `replace` | `(scene: Scene, transition: Transition \| None = None) -> None` | Replace top scene. Calls `old.on_exit()` then `scene.on_enter()`. |
| `clear` | `() -> None` | Pop all scenes (no transition support). Calls `on_exit()` on each. |

### Frame Methods

| Method | Signature | Description |
|---|---|---|
| `process_pending` | `() -> None` | Execute all queued transitions. Skipped if a transition is currently running. |
| `update` | `(dt: float) -> None` | Update active transition (if any), update current scene, then `process_pending()`. |
| `draw` | `(renderer: Renderer) -> None` | Draw current scene, then draw transition overlay (if any). |

### Scene Stack Behavior

```
push(A):       stack = [A]           A.on_enter()
push(B):       stack = [A, B]        A.on_pause(), B.on_enter()
pop():         stack = [A]           B.on_exit(), A.on_resume()
replace(C):    stack = [C]           A.on_exit(), C.on_enter()
clear():       stack = []            C.on_exit()
```

### Transition Handling

When a transition is provided, the scene change is deferred to the transition's midpoint:
1. Transition starts, `update(dt)` calls `transition.update(dt)`.
2. When `transition.at_midpoint` becomes `True`, the scene action executes (push/pop/replace).
3. When `transition.is_complete`, the transition is cleared.

---

## Class: `Transition` (abstract base)

**File**: `transition.py`
**Import**: `from engine.scene.transition import Transition`
**Base**: `ABC`

Base class for scene transitions.

### Constructor

```python
Transition(duration: float = 0.5)
```

### Properties

| Property | Type | Description |
|---|---|---|
| `duration` | `float` | Total transition time in seconds |
| `progress` | `float` | 0.0 to 1.0. Returns 1.0 if duration <= 0. |
| `is_complete` | `bool` | `True` when `elapsed >= duration` |

### Methods

| Method | Signature | Description |
|---|---|---|
| `update` | `(dt: float) -> None` | Advance elapsed time |
| `draw` | `(renderer) -> None` | **Abstract.** Draw the transition effect. Called after scene draw. |

---

## Class: `FadeTransition`

**File**: `transition.py`
**Import**: `from engine.scene.transition import FadeTransition`
**Inherits**: `Transition`

Fade to a color (default black) and back. Scene switches at midpoint (`progress >= 0.5`).

### Constructor

```python
FadeTransition(duration: float = 0.5, color: Color | None = None)  # default color: Color.BLACK
```

### Properties

| Property | Type | Description |
|---|---|---|
| `at_midpoint` | `bool` | `True` when `progress >= 0.5` |

### Behavior

- First half (progress 0.0 to 0.5): Fade out -- alpha increases 0 to 255.
- Second half (progress 0.5 to 1.0): Fade in -- alpha decreases 255 to 0.

### Usage

```python
scenes.replace(NextScene(), transition=FadeTransition(0.8))
scenes.push(PauseScene(), transition=FadeTransition(0.3, Color.WHITE))
```

---

## Class: `SlideTransition`

**File**: `transition.py`
**Import**: `from engine.scene.transition import SlideTransition`
**Inherits**: `Transition`

Slide transition providing offset values. Scene switches at midpoint.

### Constructor

```python
SlideTransition(duration: float = 0.5, direction: str = "left")
```

### Properties

| Property | Type | Description |
|---|---|---|
| `direction` | `str` | One of: `"left"`, `"right"`, `"up"`, `"down"` |
| `at_midpoint` | `bool` | `True` when `progress >= 0.5` |
| `offset_x` | `float` | Horizontal offset based on progress and direction |
| `offset_y` | `float` | Vertical offset based on progress and direction |

### Usage

```python
scenes.replace(NextScene(), transition=SlideTransition(0.5, "left"))
```
