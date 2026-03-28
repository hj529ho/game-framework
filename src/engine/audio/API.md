# engine.audio -- API Reference

## Class: `Sound`

**File**: `audio.py`
**Import**: `from engine.audio import Sound`

Short sound effect. Loads via ResourceManager on first play.

### Constructor

```python
Sound(path: str)
```

### Methods

| Method | Signature | Description |
|---|---|---|
| `play` | `(volume: float = 1.0, loops: int = 0)` | Play the sound. volume: 0.0-1.0. loops: 0=once, -1=forever. |
| `stop` | `()` | Stop playback. |

### Properties

| Property | Type | Description |
|---|---|---|
| `is_playing` | `bool` | Whether this sound is currently playing. |

### Usage

```python
class JumpBehavior(Component):
    def on_start(self):
        self.jump_sound = Sound("sfx/jump.wav")

    def on_update(self, dt):
        if current_app().keyboard.is_just_pressed(Key.SPACE):
            self.jump_sound.play(volume=0.8)
```

---

## Class: `Music`

**File**: `audio.py`
**Import**: `from engine.audio import Music`

Streaming background music. Static methods — only one track plays at a time.

### Static Methods

| Method | Signature | Description |
|---|---|---|
| `play` | `(path: str, volume: float = 1.0, loops: int = -1, fade_in_ms: int = 0)` | Play BGM. loops: -1=loop, 0=once. |
| `stop` | `(fade_out_ms: int = 0)` | Stop music. Optional fade out. |
| `pause` | `()` | Pause music. |
| `resume` | `()` | Resume paused music. |
| `set_volume` | `(volume: float)` | Set volume 0.0-1.0. |
| `is_playing` | `() -> bool` | True if playing and not paused. |
| `is_paused` | `() -> bool` | True if paused. |

### Usage

```python
class GameScene(Scene):
    def on_enter(self):
        Music.play("music/bgm.mp3", volume=0.6, fade_in_ms=1000)

    def on_exit(self):
        Music.stop(fade_out_ms=500)
```
