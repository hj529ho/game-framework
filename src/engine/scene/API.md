# engine.scene — API Reference

## Class: `Scene`

**File**: `scene.py`
**Import**: `from engine.scene import Scene`

Owns a `World` of entities. Subclass for custom scenes, or use directly. User calls `update()`/`draw()` from their own loop.

### Constructor

```python
Scene(name: str = "")  # defaults to class name if empty
```

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `name` | `str` | no | Scene name |
| `world` | `World` | no | Entity container |

### Entity Convenience Methods

Delegates to `self.world`:

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add` | `(entity: Entity)` | `Entity` | Add entity to this scene's world |
| `remove` | `(entity: Entity)` | `None` | Remove entity from this scene's world |
| `find` | `(name: str)` | `Entity \| None` | Find entity by name |
| `find_by_tag` | `(tag: str)` | `list[Entity]` | Find entities by tag |
| `find_by_type` | `(entity_type: type[T])` | `list[T]` | Find entities by type |

### Lifecycle Hooks (override in subclass)

| Hook | Signature | When Called |
|---|---|---|
| `on_enter` | `()` | Scene becomes active (pushed or replaces another) |
| `on_exit` | `()` | Scene is removed from the stack (popped or replaced) |
| `on_pause` | `()` | Another scene is pushed on top of this one |
| `on_resume` | `()` | Scene above this one was popped |

### Frame Methods

| Method | Signature | Description |
|---|---|---|
| `update` | `(dt: float)` | Calls `self.world.update(dt)`. Override to add custom logic. |
| `draw` | `(renderer: Renderer)` | Calls `self.world.draw(renderer)`. Override to add custom drawing. |

### Usage

```python
class GameScene(Scene):
    def on_enter(self):
        player = Player("player")
        player.position = Vector2(400, 300)
        self.add(player)

    def on_exit(self):
        self.world.clear()
```

---

## Class: `SceneManager`

**File**: `scene_manager.py`
**Import**: `from engine.scene import SceneManager`

Stack-based scene manager with deferred transitions. Scene changes are queued and processed after the current frame's update.

### Constructor

```python
SceneManager()
```

### Properties

| Property | Type | Description |
|---|---|---|
| `current` | `Scene \| None` | Top of the stack, or None if empty |
| `stack_depth` | `int` | Number of scenes on the stack |
| `transitioning` | `bool` | True if a transition is currently running |

### Transition Methods

All transitions are **deferred**. Pass an optional `Transition` for animated scene changes.

| Method | Signature | Description |
|---|---|---|
| `push` | `(scene, transition=None)` | Push scene on top. |
| `pop` | `(transition=None)` | Pop top scene. |
| `replace` | `(scene, transition=None)` | Replace top scene. |
| `clear` | `()` | Pop all scenes (no transition). |

### Frame Methods

| Method | Signature | Description |
|---|---|---|
| `process_pending` | `()` | Execute all queued transitions. Call manually, or let `update()` call it. |
| `update` | `(dt: float)` | Update current scene, then `process_pending()`. |
| `draw` | `(renderer: Renderer)` | Draw current scene. |

### Scene Stack Behavior

```
push(A):        stack = [A]           A.on_enter()
push(B):        stack = [A, B]        A.on_pause(), B.on_enter()
pop():          stack = [A]           B.on_exit(), A.on_resume()
replace(C):     stack = [C]           A.on_exit(), C.on_enter()
clear():        stack = []            C.on_exit()
```

### Usage

```python
scenes = SceneManager()
scenes.push(GameScene())
scenes.process_pending()  # must call to activate first scene

while app.running:
    app.poll_events()
    dt = app.clock.tick()

    if app.keyboard.is_just_pressed(Key.ESCAPE):
        if scenes.stack_depth > 1:
            scenes.pop()
        else:
            app.quit()

    scenes.update(dt)
    app.renderer.begin_frame()
    scenes.draw(app.renderer)
    app.renderer.end_frame()
```

---

## Class: `Transition` (abstract base)

**File**: `transition.py`

Base class for scene transitions.

### Constructor

```python
Transition(duration: float = 0.5)
```

### Properties

| Property | Type | Description |
|---|---|---|
| `duration` | `float` | Total transition time in seconds |
| `progress` | `float` | 0.0 to 1.0 |
| `is_complete` | `bool` | True when elapsed >= duration |

### Abstract Method

| Method | Signature |
|---|---|
| `draw` | `(renderer) -> None` |

---

## Class: `FadeTransition`

**Inherits**: `Transition`

Fade to color and back. Scene switches at midpoint (progress=0.5).

```python
FadeTransition(duration: float = 0.5, color: Color | None = None)
```

| Property | Type | Description |
|---|---|---|
| `at_midpoint` | `bool` | True when progress >= 0.5 |

### Usage

```python
# Fade to black over 0.8 seconds
scenes.replace(NextScene(), transition=FadeTransition(0.8))
```

---

## Class: `SlideTransition`

**Inherits**: `Transition`

Slide scenes in a direction.

```python
SlideTransition(duration: float = 0.5, direction: str = "left")
```

Directions: `"left"`, `"right"`, `"up"`, `"down"`
