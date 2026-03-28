# engine -- Top-level API Reference

## Module: `engine`

Re-exports all public symbols. Import everything from here.

```python
import engine
```

### Exported Symbols

| Symbol | Source Module | Type |
|---|---|---|
| `Lifecycle` | `engine.core.lifecycle` | class |
| `Game` | `engine.core.game` | class |
| `App` | `engine.core.app` | class |
| `current_app` | `engine.core.app` | function -> App |
| `Clock` | `engine.core.clock` | class |
| `Vector2` | `engine.math.vector2` | class |
| `Rect` | `engine.math.rect` | class |
| `Circle` | `engine.math.circle` | class |
| `Transform2D` | `engine.math.transform` | class |
| `Key` | `engine.input.keys` | IntEnum |
| `MouseButton` | `engine.input.keys` | IntEnum |
| `Keyboard` | `engine.input.keyboard` | class |
| `Mouse` | `engine.input.mouse` | class |
| `Renderer` | `engine.renderer.renderer` | class |
| `Color` | `engine.renderer.color` | class |
| `Entity` | `engine.ecs.entity` | class |
| `Component` | `engine.ecs.component` | class |
| `World` | `engine.ecs.world` | class |
| `Scene` | `engine.scene.scene` | class |
| `SceneManager` | `engine.scene.scene_manager` | class |

### Design Principles

- **Engine-managed lifecycle**: `Game.run()` runs the game loop. Developers define behavior through `Component` lifecycle hooks.
- **Unity-like component pattern**: `Lifecycle` base class -> `Component` -> attach to `Entity`. Entity is a pure container (like GameObject).
- **SDL2 backend**: All windowing, input, rendering uses PySDL2 (direct SDL2 bindings).
- **Deferred draw queue**: Renderer collects draw commands, sorts by layer, then executes in `end_frame()`.

### Lifecycle Order Per Frame

```
Game.run() loop:
  1. App.poll_events()                       -- SDL event polling, input state update
  2. Clock.tick()                            -- delta time calculation
  3. Scene.update(dt):
     a. World._process_additions()           -- add queued entities
     b. Component.on_start()                 -- first frame only, for new components
     c. Component.on_fixed_update(fixed_dt)  -- 0~N times (accumulator, default 1/50s)
     d. Component.on_update(dt)              -- once per frame
     e. Component.on_late_update(dt)         -- after all updates
     f. World._process_removals()            -- remove queued entities + on_destroy
  4. Renderer.begin_frame()                  -- clear screen
  5. Scene.draw(renderer):
     a. Component.on_draw(renderer)          -- for all active components
  6. Renderer.end_frame()                    -- sort by layer, execute, present
  7. SceneManager.process_pending()          -- scene transitions
```
