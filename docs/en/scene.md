# Scene Management

The `engine.scene` module provides `Scene` (a container that owns a `World` of
entities) and `SceneManager` (a stack-based system for transitioning between
scenes). Together, they let you organize your game into distinct states like
title screen, gameplay, pause menu, and game over.

---

## Scene

A `Scene` owns a `World` and provides lifecycle hooks for entering, exiting,
pausing, and resuming. You subclass `Scene` and override the hooks to set up and
tear down your game state. Entity behavior is defined in Components, not in
Scene.

### Creating a scene

```python
import engine


class PlayerMovement(engine.Component):
    def on_start(self):
        self.speed = 300.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        d = engine.Vector2.zero()
        if kb.is_pressed(engine.Key.LEFT):  d = d + engine.Vector2.left()
        if kb.is_pressed(engine.Key.RIGHT): d = d + engine.Vector2.right()
        if kb.is_pressed(engine.Key.UP):    d = d + engine.Vector2.up()
        if kb.is_pressed(engine.Key.DOWN):  d = d + engine.Vector2.down()
        if d.magnitude > 0:
            self.transform.translate(d.normalized * self.speed * dt)


class PlayerRenderer(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(p.x - 20, p.y - 20, 40, 40, engine.Color.BLUE)


class GameScene(engine.Scene):
    def on_enter(self):
        """Called when this scene becomes active."""
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_component(PlayerMovement())
        player.add_component(PlayerRenderer())
        self.add(player)

        for i in range(5):
            enemy = engine.Entity(f"enemy_{i}")
            enemy.position = engine.Vector2(100 + i * 150, 100)
            enemy.add_component(PatrolMovement())
            enemy.add_component(EnemyRenderer())
            self.add(enemy)

    def on_exit(self):
        """Called when this scene is removed from the stack."""
        self.world.clear()
```

### What a Scene owns

Each Scene has one `World` instance. The World manages all entities for that
scene. When you add an entity to a scene, it goes into that scene's world.

```
Scene
  |
  +-- World
        |
        +-- Entity (Player)     [PlayerMovement, PlayerRenderer]
        +-- Entity (enemy_0)    [PatrolMovement, EnemyRenderer]
        +-- Entity (enemy_1)    [PatrolMovement, EnemyRenderer]
        +-- Entity (enemy_2)    [PatrolMovement, EnemyRenderer]
```

### Entity convenience methods

Scene delegates entity operations to its world, so you do not need to type
`self.world.add(...)` every time:

```python
self.add(entity)                     # same as self.world.add(entity)
self.remove(entity)                  # same as self.world.remove(entity)
self.find("Player")                  # same as self.world.find_by_name("Player")
self.find_by_tag("enemy")           # same as self.world.find_by_tag("enemy")
self.find_with_component(Health)    # same as self.world.find_with_component(Health)
```

### Lifecycle hooks

| Hook | When called | Typical use |
|---|---|---|
| `on_enter()` | Scene becomes active (pushed onto stack or replaces another) | Spawn entities, start music |
| `on_exit()` | Scene is removed from the stack (popped or replaced) | Clear entities, stop music, save |
| `on_pause()` | Another scene is pushed on top of this one | Pause timers, dim display |
| `on_resume()` | The scene above is popped, this scene is active again | Resume timers, restore state |

### Frame methods

The engine calls these each frame via `Game.run()`:

```python
scene.update(dt)          # calls self.world.update(dt)
scene.draw(renderer)      # calls self.world.draw(renderer)
```

You can override `update` and `draw` to add scene-level logic:

```python
class GameScene(engine.Scene):
    def update(self, dt):
        super().update(dt)  # update all entity components
        self.check_win_condition()

    def draw(self, renderer):
        super().draw(renderer)  # draw all entity components
        self.draw_hud(renderer)

    def draw_hud(self, renderer):
        renderer.draw_rect(10, 10, 200, 20, engine.Color.DARK_GRAY, layer=10)
```

---

## SceneManager

`SceneManager` maintains a stack of scenes. Only the scene on top of the stack
is updated and drawn. Transitions between scenes are **deferred** -- they are
queued and processed after the current frame's update completes. The
`SceneManager` is created internally by `Game` and accessed via `game.scenes`.

### Properties

```python
game.scenes.current       # The top scene on the stack (or None if empty)
game.scenes.stack_depth   # Number of scenes on the stack
```

### Transition methods

All transitions are deferred. They queue an action that executes during
`process_pending()` (which the engine calls automatically at the end of each
frame).

#### `push(scene)` -- Add a scene on top

```python
game.scenes.push(PauseScene())
```

The current top scene receives `on_pause()`. The new scene receives `on_enter()`
and becomes the active scene.

#### `pop()` -- Remove the top scene

```python
game.scenes.pop()
```

The top scene receives `on_exit()`. The scene below it (if any) receives
`on_resume()` and becomes the active scene.

#### `replace(scene)` -- Swap the top scene

```python
game.scenes.replace(GameOverScene())
```

The current top scene receives `on_exit()`. The new scene receives `on_enter()`.
The stack depth stays the same.

#### `clear()` -- Remove all scenes

```python
game.scenes.clear()
```

All scenes are popped in LIFO (last-in-first-out) order. Each receives
`on_exit()`.

### Deferred transitions

Transitions do not happen immediately when you call `push()`, `pop()`, etc.
They are queued and processed later. This prevents bugs that would occur if
scene transitions happened in the middle of an update.

### Using scene transitions from Components

Components can trigger scene transitions by holding a reference to the `Game`
instance or its `SceneManager`:

```python
class PauseToggle(engine.Component):
    def on_awake(self):
        self.game_ref = game  # reference to the Game instance

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        if kb.is_just_pressed(engine.Key.ESCAPE):
            sm = self.game_ref.scenes
            if sm.stack_depth == 1:
                sm.push(PauseScene())
            else:
                sm.pop()
```

---

## Scene Stack Behavior

The stack model makes it natural to layer scenes. Here is a visual walkthrough:

### Starting up

```
game.run(TitleScene())

Stack: [ TitleScene ]
              ^
              |
           active
```

`TitleScene.on_enter()` is called.

### Transitioning to gameplay

```
game.scenes.replace(GameScene())
-- after process_pending() --

Stack: [ GameScene ]
             ^
             |
          active
```

`TitleScene.on_exit()` is called, then `GameScene.on_enter()`.

### Opening a pause menu

```
game.scenes.push(PauseScene())
-- after process_pending() --

Stack: [ GameScene, PauseScene ]
                        ^
                        |
                     active
```

`GameScene.on_pause()` is called, then `PauseScene.on_enter()`.

The GameScene still exists in memory but is not updated or drawn. Only the top
scene (PauseScene) is active.

### Closing the pause menu

```
game.scenes.pop()
-- after process_pending() --

Stack: [ GameScene ]
             ^
             |
          active
```

`PauseScene.on_exit()` is called, then `GameScene.on_resume()`.

The game continues exactly where it left off.

### Full lifecycle diagram

```
push(A)     push(B)     pop()       replace(C)   clear()
   |           |          |             |            |
   v           v          v             v            v

[A]        [A, B]       [A]           [C]          []
 ^              ^         ^             ^
 A.on_enter  A.on_pause  B.on_exit   A.on_exit   C.on_exit
             B.on_enter  A.on_resume C.on_enter
```

### Hook call order reference

| Transition | Hook calls (in order) |
|---|---|
| `push(B)` when A is on top | `A.on_pause()`, `B.on_enter()` |
| `pop()` when B is on top of A | `B.on_exit()`, `A.on_resume()` |
| `replace(C)` when A is on top | `A.on_exit()`, `C.on_enter()` |
| `clear()` with [A, B, C] on stack | `C.on_exit()`, `B.on_exit()`, `A.on_exit()` |
| `push(A)` on empty stack | `A.on_enter()` |
| `pop()` on single-scene stack [A] | `A.on_exit()` |

---

## Common Scene Patterns

### Pattern 1: Title screen -> Gameplay

Scene transitions are triggered from Components:

```python
class TitleController(engine.Component):
    def on_awake(self):
        self.game_ref = game

    def on_update(self, dt):
        if engine.current_app().keyboard.is_just_pressed(engine.Key.RETURN):
            self.game_ref.scenes.replace(GameScene())


class TitleScene(engine.Scene):
    def on_enter(self):
        controller = engine.Entity("Controller")
        controller.add_component(TitleController())
        self.add(controller)

        # Add title screen visuals...

    def on_exit(self):
        self.world.clear()
```

### Pattern 2: Pause menu overlay

```python
class PauseController(engine.Component):
    def on_awake(self):
        self.game_ref = game

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        if kb.is_just_pressed(engine.Key.ESCAPE):
            # Pop the pause menu to resume the game
            self.game_ref.scenes.pop()
        if kb.is_just_pressed(engine.Key.Q):
            # Quit to title
            self.game_ref.scenes.clear()
            self.game_ref.scenes.push(TitleScene())


class PauseOverlay(engine.Component):
    def on_draw(self, renderer):
        # Semi-transparent overlay
        renderer.draw_rect(0, 0, 800, 600, engine.Color(0, 0, 0, 128), layer=10)
        # Menu items
        renderer.draw_rect(300, 250, 200, 40, engine.Color.DARK_GRAY, layer=11)
        renderer.draw_rect(300, 310, 200, 40, engine.Color.DARK_GRAY, layer=11)


class PauseScene(engine.Scene):
    def on_enter(self):
        ui = engine.Entity("PauseUI")
        ui.add_component(PauseController())
        ui.add_component(PauseOverlay())
        self.add(ui)

    def on_exit(self):
        self.world.clear()
```

### Pattern 3: Game over with retry

```python
class GameOverController(engine.Component):
    def on_awake(self):
        self.game_ref = game

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        if kb.is_just_pressed(engine.Key.R):
            # Replace with a fresh GameScene
            self.game_ref.scenes.replace(GameScene())
        if kb.is_just_pressed(engine.Key.ESCAPE):
            # Return to title
            self.game_ref.scenes.clear()
            self.game_ref.scenes.push(TitleScene())


class GameOverScene(engine.Scene):
    def on_enter(self):
        ui = engine.Entity("GameOverUI")
        ui.add_component(GameOverController())
        ui.add_component(GameOverRenderer())
        self.add(ui)

    def on_exit(self):
        self.world.clear()
```

---

## Full Example: A Game with Multiple Scenes

Here is a complete example with a title scene, a game scene with a player and
enemies, and a pause menu.

```python
import engine
import math


# ---- Components ----

class Movement(engine.Component):
    def on_start(self):
        self.speed = 300.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        d = engine.Vector2.zero()
        if kb.is_pressed(engine.Key.A) or kb.is_pressed(engine.Key.LEFT):
            d = d + engine.Vector2.left()
        if kb.is_pressed(engine.Key.D) or kb.is_pressed(engine.Key.RIGHT):
            d = d + engine.Vector2.right()
        if kb.is_pressed(engine.Key.W) or kb.is_pressed(engine.Key.UP):
            d = d + engine.Vector2.up()
        if kb.is_pressed(engine.Key.S) or kb.is_pressed(engine.Key.DOWN):
            d = d + engine.Vector2.down()
        if d.magnitude > 0:
            self.transform.translate(d.normalized * self.speed * dt)

        # Clamp to screen
        from engine.math.utils import clamp
        self.position = engine.Vector2(
            clamp(self.position.x, 20, 780),
            clamp(self.position.y, 20, 580),
        )


class SineWave(engine.Component):
    def on_start(self):
        self.timer = 0.0
        self.start_pos = self.position.copy()

    def on_update(self, dt):
        self.timer += dt
        self.position = self.start_pos + engine.Vector2(
            math.sin(self.timer * 2) * 80, 0,
        )


class BoxRenderer(engine.Component):
    def on_awake(self):
        self.color = engine.Color.BLUE
        self.size = 40

    def on_draw(self, renderer):
        p = self.position
        half = self.size / 2
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size, self.color)


class SceneTransitioner(engine.Component):
    """Handles scene transitions. Requires a game_ref set in on_awake."""

    def on_awake(self):
        self.game_ref = None  # set by caller
        self.push_scene_fn = None
        self.pop_key = None
        self.push_key = None

    def on_update(self, dt):
        if self.game_ref is None:
            return
        kb = engine.current_app().keyboard
        if self.pop_key and kb.is_just_pressed(self.pop_key):
            self.game_ref.scenes.pop()
        if self.push_key and kb.is_just_pressed(self.push_key) and self.push_scene_fn:
            self.game_ref.scenes.push(self.push_scene_fn())


class QuitOnKey(engine.Component):
    def on_awake(self):
        self.quit_key = engine.Key.ESCAPE

    def on_update(self, dt):
        if engine.current_app().keyboard.is_just_pressed(self.quit_key):
            engine.current_app().quit()


# ---- Scenes ----

class TitleScene(engine.Scene):
    def on_enter(self):
        # Title visuals
        title_box = engine.Entity("TitleBox")
        box = title_box.add_component(BoxRenderer())
        box.color = engine.Color.DARK_GRAY
        box.size = 400
        title_box.position = engine.Vector2(400, 200)
        self.add(title_box)

        # Controller: ENTER -> start game, ESCAPE -> quit
        controller = engine.Entity("Controller")
        controller.add_component(QuitOnKey())
        self.add(controller)

    def on_exit(self):
        self.world.clear()


class GameScene(engine.Scene):
    def on_enter(self):
        # Player
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 400)
        player.add_component(Movement())
        player.add_tag("player")
        box = player.add_component(BoxRenderer())
        box.color = engine.Color.BLUE
        box.size = 40
        self.add(player)

        # Enemies
        for i in range(4):
            enemy = engine.Entity(f"enemy_{i}")
            enemy.position = engine.Vector2(100 + i * 200, 150)
            enemy.add_component(SineWave())
            enemy.add_tag("enemy")
            box = enemy.add_component(BoxRenderer())
            box.color = engine.Color.RED
            box.size = 30
            self.add(enemy)

        # Controller
        controller = engine.Entity("Controller")
        controller.add_component(QuitOnKey())
        self.add(controller)

    def on_pause(self):
        print("Game paused")

    def on_resume(self):
        print("Game resumed")

    def on_exit(self):
        self.world.clear()


class PauseScene(engine.Scene):
    def on_enter(self):
        overlay = engine.Entity("PauseOverlay")
        overlay.position = engine.Vector2(400, 300)
        box = overlay.add_component(BoxRenderer())
        box.color = engine.Color.GRAY
        box.size = 200
        self.add(overlay)

    def on_exit(self):
        self.world.clear()


# ---- Main ----

game = engine.Game(title="Scene Demo", width=800, height=600, fps=60)


class PauseToggle(engine.Component):
    """Push/pop pause scene with SPACE."""

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        if kb.is_just_pressed(engine.Key.SPACE):
            sm = game.scenes
            if sm.stack_depth == 1:
                sm.push(PauseScene())
            else:
                sm.pop()


class TitleStartGame(engine.Component):
    """Replace title with game scene on ENTER."""

    def on_update(self, dt):
        if engine.current_app().keyboard.is_just_pressed(engine.Key.RETURN):
            game.scenes.replace(MainScene())


# Wrap GameScene to add PauseToggle
class MainScene(GameScene):
    def on_enter(self):
        super().on_enter()
        controller = self.find("Controller")
        if controller:
            controller.add_component(PauseToggle())


# Wrap TitleScene to add start-game logic
class MainTitleScene(TitleScene):
    def on_enter(self):
        super().on_enter()
        controller = self.find("Controller")
        if controller:
            controller.add_component(TitleStartGame())


game.run(MainTitleScene())
```

### How this example flows

```
1. Game starts -> MainTitleScene is pushed and activated
   Stack: [MainTitleScene]

2. User presses ENTER -> MainTitleScene replaces itself with MainScene
   Stack: [MainScene]
   Hooks: MainTitleScene.on_exit(), MainScene.on_enter()

3. User presses SPACE -> PauseScene is pushed on top
   Stack: [MainScene, PauseScene]
   Hooks: MainScene.on_pause(), PauseScene.on_enter()
   Note: MainScene is still in memory, but not updated or drawn

4. User presses SPACE again -> PauseScene is popped
   Stack: [MainScene]
   Hooks: PauseScene.on_exit(), MainScene.on_resume()

5. User presses ESCAPE -> game quits
```

---

## Tips

### Scene-specific input handling via Components

Put scene-specific input handling in Components attached to entities in that
scene, not in the Scene subclass directly. This keeps behavior in Components
and makes scenes lightweight setup/teardown containers:

```python
class GameSceneController(engine.Component):
    def on_update(self, dt):
        if engine.current_app().keyboard.is_just_pressed(engine.Key.ESCAPE):
            game.scenes.push(PauseScene())
```

### Clean up in `on_exit`

Always call `self.world.clear()` in `on_exit()` if your scene creates entities
in `on_enter()`. This ensures entity components are properly destroyed and do
not leak.

### Only the top scene is updated

The SceneManager only calls `update()` and `draw()` on the top scene. If you
push a pause menu on top of the game, the game scene is **not** updated --
entity components freeze in place. This is usually the desired behavior. If you
need the game to continue updating (e.g., for an animated background), you would
need to handle that explicitly.

### All behavior in Components

The engine follows a strict rule: Entity is a pure container, all logic goes in
Components. When building scenes, create entities, attach Components that define
behavior, and add them to the scene. The Scene itself should only handle
`on_enter` / `on_exit` setup and teardown.

---

## Where to Go Next

| Topic | Document |
|---|---|
| Getting started with the engine | [Getting Started](getting-started.md) |
| Overall architecture and design | [Architecture](architecture.md) |
| Entities, components, worlds | [ECS](ecs.md) |
| Renderer, draw queue, colors, layers | [Rendering](rendering.md) |
