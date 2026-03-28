# engine -- Top-Level API Reference

A 2D game engine built on SDL2 with Unity-style components, an ECS architecture, CSS-based UI, and a fixed-timestep game loop.

**Version:** 0.1.0

---

## Design Principles

1. **Unity-style Components** -- All gameplay logic lives in `Component` subclasses attached to `Entity` containers. Entity itself has no behavior.
2. **Lifecycle hooks** -- 7 hooks called automatically: `on_awake`, `on_start`, `on_fixed_update`, `on_update`, `on_late_update`, `on_draw`, `on_destroy`.
3. **Fixed timestep** -- `on_fixed_update` runs at a fixed interval (default 1/50s) via an accumulator, independent of frame rate.
4. **Scene stack** -- `SceneManager` manages a stack of scenes with push/pop/replace and optional transitions.
5. **CSS-based UI** -- The `ui` module provides a DOM-like element tree with flexbox layout, CSS string parsing, and stylesheets.
6. **Single entry point** -- `Game.run(initial_scene)` starts the entire engine.

---

## Frame Lifecycle Order

```
Game.run(initial_scene)
  |
  +-- SceneManager.push(initial_scene) -> Scene.on_enter()
  |
  +-- while app.running:
        |
        1. App.poll_events()           -- SDL events, input state updated
        2. Clock.tick()                -- delta time calculated
        3. SceneManager.update(dt)
           |
           +-- Scene.update(dt) -> World.update(dt)
                 |
                 a. Process pending entity additions
                 b. Component.on_start() for new components
                 c. Component.on_fixed_update(fixed_dt)  [0..N times, accumulator]
                 d. Component.on_update(dt)
                 e. Component.on_late_update(dt)
                 f. Process pending entity removals
        |
        4. Renderer.begin_frame()      -- clear screen
        5. SceneManager.draw(renderer)
           |
           +-- Scene.draw(renderer) -> World.draw(renderer)
                 +-- Component.on_draw(renderer)
        |
        6. Renderer.end_frame()        -- sort draw queue, present frame
        7. SceneManager.process_pending() -- scene transitions
  |
  +-- Cleanup: scenes.clear(), app.destroy()
```

---

## Exported Symbols

All symbols below are importable directly from `engine`:

```python
from engine import Game, Scene, Entity, Component, Vector2, Color
```

| Symbol | Module | Kind |
|---|---|---|
| `Lifecycle` | `engine.core.lifecycle` | Class |
| `App` | `engine.core.app` | Class |
| `current_app` | `engine.core.app` | Function `() -> App` |
| `Clock` | `engine.core.clock` | Class |
| `Game` | `engine.core.game` | Class |
| `Event` | `engine.core.events` | Dataclass (frozen) |
| `EventBus` | `engine.core.events` | Class |
| `get_event_bus` | `engine.core.events` | Function `() -> EventBus` |
| `Vector2` | `engine.math.vector2` | Class |
| `Rect` | `engine.math.rect` | Class |
| `Circle` | `engine.math.circle` | Class |
| `Transform2D` | `engine.math.transform` | Class |
| `EASINGS` | `engine.math.easing` | `dict[str, callable]` (28 entries) |
| `Key` | `engine.input.keys` | IntEnum |
| `MouseButton` | `engine.input.keys` | IntEnum |
| `Keyboard` | `engine.input.keyboard` | Class |
| `Mouse` | `engine.input.mouse` | Class |
| `Renderer` | `engine.renderer.renderer` | Class |
| `Color` | `engine.renderer.color` | Class |
| `SpriteRenderer` | `engine.renderer.sprite` | Component |
| `TextRenderer` | `engine.renderer.text` | Component |
| `Camera2D` | `engine.renderer.camera` | Component |
| `AnimatedSprite` | `engine.renderer.animated_sprite` | Component |
| `Animation` | `engine.renderer.animated_sprite` | Dataclass |
| `Entity` | `engine.ecs.entity` | Class |
| `Component` | `engine.ecs.component` | Class |
| `World` | `engine.ecs.world` | Class |
| `Scene` | `engine.scene.scene` | Class |
| `SceneManager` | `engine.scene.scene_manager` | Class |
| `Transition` | `engine.scene.transition` | ABC |
| `FadeTransition` | `engine.scene.transition` | Class |
| `SlideTransition` | `engine.scene.transition` | Class |
| `ResourceManager` | `engine.resources.resource_manager` | Class |
| `Sound` | `engine.audio.audio` | Class |
| `Music` | `engine.audio.audio` | Class (static API) |
| `Collider` | `engine.physics.collider` | Component (base) |
| `BoxCollider` | `engine.physics.collider` | Component |
| `CircleCollider` | `engine.physics.collider` | Component |
| `CollisionInfo` | `engine.physics.collision` | Dataclass |
| `RaycastHit` | `engine.physics.collision` | Dataclass |
| `test_collision` | `engine.physics.collision` | Function |
| `raycast` | `engine.physics.collision` | Function |
| `raycast_all` | `engine.physics.collision` | Function |
| `PhysicsWorld` | `engine.physics.physics_world` | Component |
| `AnimationClip` | `engine.animation.clip` | Dataclass |
| `FrameEvent` | `engine.animation.clip` | Dataclass |
| `AnimatorStateMachine` | `engine.animation.state_machine` | Class |
| `Animator` | `engine.animation.animator` | Component |
| `Tween` | `engine.tween.tween` | Class |
| `TweenSequence` | `engine.tween.tween` | Class |
| `TweenParallel` | `engine.tween.tween` | Class |
| `TweenManager` | `engine.tween.tween` | Component |
| `LoopType` | `engine.tween.tween` | Enum |
| `ui` | `engine.ui` | Module |
| `Style` | `engine.ui.core.style` | Class |
| `EdgeInsets` | `engine.ui.core.style` | Dataclass |
| `px` | `engine.ui.core.units` | Function `(float) -> Unit` |
| `pct` | `engine.ui.core.units` | Function `(float) -> Unit` |
| `auto` | `engine.ui.core.units` | `Unit` constant |
| `Element` | `engine.ui.core.element` | Class |
| `Div` | `engine.ui.elements.div` | Class |
| `UIText` | `engine.ui.elements.text` | Class (aliased from `Text`) |
| `UIImage` | `engine.ui.elements.image` | Class (aliased from `Image`) |
| `Button` | `engine.ui.elements.button` | Class |
| `ProgressBar` | `engine.ui.elements.progress_bar` | Class |
| `UIRoot` | `engine.ui.ui_root` | Component |
| `UIEvent` | `engine.ui.events` | Dataclass |
| `ClickEvent` | `engine.ui.events` | Dataclass |

---

## Quick Start Example

```python
from engine import Game, Scene, Entity, Component, Vector2, Key, Color, SpriteRenderer, current_app

class PlayerMovement(Component):
    def on_start(self):
        self.speed = 200.0

    def on_update(self, dt):
        kb = current_app().keyboard
        vel = Vector2.zero()
        if kb.is_pressed(Key.W): vel = vel + Vector2.up()
        if kb.is_pressed(Key.S): vel = vel + Vector2.down()
        if kb.is_pressed(Key.A): vel = vel + Vector2.left()
        if kb.is_pressed(Key.D): vel = vel + Vector2.right()
        if vel.sqr_magnitude > 0:
            self.transform.translate(vel.normalized * self.speed * dt)

class GameScene(Scene):
    def on_enter(self):
        player = Entity("Player")
        player.position = Vector2(400, 300)
        player.add_component(PlayerMovement())
        player.add_component(SpriteRenderer("player.png"))
        self.add(player)

game = Game(title="My Game", width=800, height=600)
game.run(GameScene())
```
