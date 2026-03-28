# Input Module

The `engine.input` module handles keyboard and mouse input using a double-buffer
pattern. It provides three query methods for each input source -- `is_pressed`,
`is_just_pressed`, and `is_just_released` -- that let you distinguish between
holding a key, tapping it, and letting it go.

---

## How Input Works: The Double-Buffer Pattern

The input system maintains two snapshots of state: the **current** frame and the
**previous** frame. Every time the engine polls events (internally, during
`Game.run()`), the following happens:

```
1. Copy current state -> previous state    (keyboard.update() / mouse.update())
2. Process all SDL events this frame       (keyboard.process_event() / mouse.process_event())
3. Now "current" has this frame's state and "previous" has last frame's state
```

By comparing the two snapshots, the system can determine edge transitions:

```
                Frame 1    Frame 2    Frame 3    Frame 4    Frame 5
User action:    [press]    [hold]     [hold]     [release]  [nothing]

previous:       False      True       True       True       False
current:        True       True       True       False      False

is_pressed:     True       True       True       False      False
is_just_pressed:True       False      False      False      False
is_just_released:False     False      False      True       False
```

### Timing diagram

```
Key state:   ___/````````````\___

Frame:        1    2    3    4    5

pressed:      Y    Y    Y    N    N
just_pressed: Y    N    N    N    N
just_released:N    N    N    Y    N
```

The three methods give you everything you need:

| Method | True when... | Use for... |
|---|---|---|
| `is_pressed` | Key is held down right now | Continuous actions: movement, charging |
| `is_just_pressed` | Key was pressed this frame (edge: off -> on) | One-shot actions: jump, shoot, menu select |
| `is_just_released` | Key was released this frame (edge: on -> off) | Release actions: throw, confirm charge |

---

## Keyboard

### Querying key state

Inside a Component, use `current_app()` to access the keyboard:

```python
class MyComponent(engine.Component):
    def on_update(self, dt):
        kb = engine.current_app().keyboard

        # Is the key held down right now?
        if kb.is_pressed(engine.Key.SPACE):
            self.charge_power += dt

        # Was the key just pressed this frame?
        if kb.is_just_pressed(engine.Key.SPACE):
            self.jump()

        # Was the key just released this frame?
        if kb.is_just_released(engine.Key.SPACE):
            self.release_charged_attack()
```

### The Key enum

The `Key` enum maps friendly names to SDL2 keycodes. Import it from `engine`:

```python
from engine import Key
```

Available keys:

| Group | Members |
|---|---|
| Letters | `Key.A` through `Key.Z` |
| Numbers | `Key.NUM_0` through `Key.NUM_9` |
| Arrows | `Key.UP`, `Key.DOWN`, `Key.LEFT`, `Key.RIGHT` |
| Special | `Key.SPACE`, `Key.RETURN`, `Key.ESCAPE`, `Key.TAB`, `Key.BACKSPACE`, `Key.DELETE` |
| Modifiers | `Key.LSHIFT`, `Key.RSHIFT`, `Key.LCTRL`, `Key.RCTRL`, `Key.LALT`, `Key.RALT` |
| Function | `Key.F1` through `Key.F12` |

The values are SDL2 `SDLK_*` constants, so they work with any keyboard layout
that SDL2 supports.

---

## Mouse

### Position

```python
class AimingComponent(engine.Component):
    def on_update(self, dt):
        mouse = engine.current_app().mouse
        pos = mouse.position  # Vector2 with current mouse position in screen pixels
```

The position is updated every frame from `SDL_MOUSEMOTION` events.

### Buttons

Mouse buttons work exactly like keyboard keys -- the same three query methods:

```python
from engine import MouseButton

class DrawTool(engine.Component):
    def on_update(self, dt):
        mouse = engine.current_app().mouse

        # Is the left button held down?
        if mouse.is_pressed(MouseButton.LEFT):
            self.draw_at(mouse.position)

        # Was the left button just clicked this frame?
        if mouse.is_just_pressed(MouseButton.LEFT):
            self.select_item(mouse.position)

        # Was the left button just released?
        if mouse.is_just_released(MouseButton.LEFT):
            self.drop_item(mouse.position)
```

### The MouseButton enum

```python
from engine import MouseButton

MouseButton.LEFT    # Left mouse button
MouseButton.MIDDLE  # Middle mouse button (scroll wheel click)
MouseButton.RIGHT   # Right mouse button
```

### Scroll wheel

```python
class ZoomComponent(engine.Component):
    def on_update(self, dt):
        scroll = engine.current_app().mouse.scroll_delta
        # positive = scroll up, negative = scroll down
        if scroll > 0:
            self.zoom_in()
        elif scroll < 0:
            self.zoom_out()
```

The scroll delta is reset to `0.0` at the beginning of each frame (during
`mouse.update()`). If the user scrolls multiple notches in one frame, the values
are accumulated.

---

## Common Input Patterns

All of these patterns go inside Component `on_update` methods. Components access
input through `current_app()`.

### 1. Four-direction movement (WASD or arrow keys)

```python
class Movement(engine.Component):
    def on_start(self):
        self.speed = 300.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        direction = engine.Vector2.zero()

        if kb.is_pressed(engine.Key.LEFT) or kb.is_pressed(engine.Key.A):
            direction = direction + engine.Vector2.left()
        if kb.is_pressed(engine.Key.RIGHT) or kb.is_pressed(engine.Key.D):
            direction = direction + engine.Vector2.right()
        if kb.is_pressed(engine.Key.UP) or kb.is_pressed(engine.Key.W):
            direction = direction + engine.Vector2.up()
        if kb.is_pressed(engine.Key.DOWN) or kb.is_pressed(engine.Key.S):
            direction = direction + engine.Vector2.down()

        # Normalize to prevent faster diagonal movement
        if direction.magnitude > 0:
            self.transform.translate(direction.normalized * self.speed * dt)
```

### 2. Jump (single press, not repeating while held)

```python
class Jumper(engine.Component):
    def on_start(self):
        self.velocity_y = 0.0
        self.on_ground = True
        self.jump_force = 400.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        if kb.is_just_pressed(engine.Key.SPACE) and self.on_ground:
            self.velocity_y = -self.jump_force
            self.on_ground = False
```

Using `is_just_pressed` ensures the entity jumps only once per key press, even
if the user holds the key down.

### 3. Shooting with cooldown

```python
class Shooter(engine.Component):
    def on_start(self):
        self.shoot_cooldown = 0.0
        self.shoot_rate = 0.15  # seconds between shots

    def on_update(self, dt):
        self.shoot_cooldown -= dt
        kb = engine.current_app().keyboard

        if kb.is_pressed(engine.Key.SPACE) and self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = self.shoot_rate

    def shoot(self):
        mouse = engine.current_app().mouse
        bullet = engine.Entity("bullet")
        bullet.position = self.position.copy()
        bullet.transform.look_at(mouse.position)
        bullet.add_component(BulletMovement())
        self.entity._world.add(bullet)
```

### 4. Charge and release

```python
class ChargeAttack(engine.Component):
    def on_start(self):
        self.charge = 0.0
        self.max_charge = 2.0

    def on_update(self, dt):
        mouse = engine.current_app().mouse

        # While holding, build up charge
        if mouse.is_pressed(engine.MouseButton.LEFT):
            self.charge = min(self.charge + dt, self.max_charge)

        # On release, fire with accumulated power
        if mouse.is_just_released(engine.MouseButton.LEFT) and self.charge > 0:
            self.fire(power=self.charge)
            self.charge = 0.0
```

### 5. Menu navigation

```python
class MenuNavigator(engine.Component):
    def on_start(self):
        self.selected = 0
        self.menu_items = ["New Game", "Load Game", "Options", "Quit"]

    def on_update(self, dt):
        kb = engine.current_app().keyboard

        if kb.is_just_pressed(engine.Key.UP):
            self.selected = (self.selected - 1) % len(self.menu_items)
        if kb.is_just_pressed(engine.Key.DOWN):
            self.selected = (self.selected + 1) % len(self.menu_items)
        if kb.is_just_pressed(engine.Key.RETURN):
            self.activate_menu_item(self.menu_items[self.selected])
```

Using `is_just_pressed` here means the selection moves one step per key press,
not one step per frame while the key is held. This gives the user precise
control.

### 6. Modifier keys (sprint, precision mode)

```python
class Movement(engine.Component):
    def on_start(self):
        self.base_speed = 200.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard

        if kb.is_pressed(engine.Key.LSHIFT):
            speed = self.base_speed * 2.0   # sprint
        elif kb.is_pressed(engine.Key.LCTRL):
            speed = self.base_speed * 0.5   # slow/precision mode
        else:
            speed = self.base_speed

        # ... use speed for movement
```

### 7. Mouse aiming

```python
class MouseAim(engine.Component):
    def on_update(self, dt):
        mouse = engine.current_app().mouse
        # Rotate to face the mouse cursor
        self.transform.look_at(mouse.position)

    def on_draw(self, renderer):
        p = self.position
        # Draw the entity
        renderer.draw_rect(p.x - 16, p.y - 16, 32, 32, engine.Color.BLUE)
        # Draw an aiming line
        aim_end = p + self.transform.forward * 60
        renderer.draw_line(p, aim_end, engine.Color.YELLOW)
```

### 8. Click detection on a rectangle

```python
class ClickableButton(engine.Component):
    def on_awake(self):
        self.button_rect = engine.Rect(300, 400, 200, 50)

    def on_update(self, dt):
        mouse = engine.current_app().mouse
        if mouse.is_just_pressed(engine.MouseButton.LEFT):
            if self.button_rect.contains_point(mouse.position):
                self.on_button_clicked()
```

### 9. Scroll wheel zoom

```python
class ZoomControl(engine.Component):
    def on_start(self):
        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 3.0

    def on_update(self, dt):
        from engine.math.utils import clamp
        scroll = engine.current_app().mouse.scroll_delta
        if scroll != 0:
            self.zoom_level += scroll * 0.1
            self.zoom_level = clamp(self.zoom_level, self.min_zoom, self.max_zoom)
```

---

## Frame Lifecycle Summary

Here is how input fits into the frame lifecycle managed by `Game.run()`:

```
Game.run() calls App.poll_events() internally:
  |
  |-- keyboard.update()          Copy current -> previous
  |-- mouse.update()             Copy current -> previous, reset scroll to 0
  |
  |-- for each SDL event:
  |     keyboard.process_event() Update current keys (KEYDOWN / KEYUP)
  |     mouse.process_event()    Update position (MOTION), buttons (DOWN/UP), scroll (WHEEL)
  |
  v
Engine calls Component.on_update(dt) on all active components:
  kb = current_app().keyboard
  kb.is_pressed(Key.W)           current contains Key.W?
  kb.is_just_pressed(Key.SPACE)  current has SPACE and previous does not?
  mouse = current_app().mouse
  mouse.position                 latest position from MOUSEMOTION events
```

The engine handles calling `poll_events()` at the right time. Your Components
just read the input state in their `on_update` methods.

---

## Where to Go Next

| Topic | Document |
|---|---|
| Renderer, draw queue, colors, layers | [Rendering](rendering.md) |
| Entities, components, worlds | [ECS](ecs.md) |
| Scenes and scene management | [Scenes](scene.md) |
