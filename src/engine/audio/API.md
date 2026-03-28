# engine.audio -- API Reference

## Class: `Sound`

**File**: `audio.py`
**Import**: `from engine.audio.audio import Sound`

Short sound effect. Loads via `ResourceManager` on first `play()`.

### Constructor

```python
Sound(path: str)
```

| Parameter | Type | Description |
|---|---|---|
| `path` | `str` | Sound file path (WAV/OGG), resolved by `ResourceManager` |

### Properties

| Property | Type | Writable | Description |
|---|---|---|---|
| `is_playing` | `bool` | no | `True` if this sound is currently playing on its channel |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `play` | `(volume: float = 1.0, loops: int = 0)` | `None` | Play the sound. `volume`: 0.0 to 1.0. `loops`: 0 = play once, -1 = loop forever, N = play N+1 times. |
| `stop` | `()` | `None` | Stop playback on the assigned channel. |

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
**Import**: `from engine.audio.audio import Music`

Streaming background music. All methods are **static** -- only one music track plays at a time (SDL_mixer limitation).

### Static Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `play` | `(path: str, volume: float = 1.0, loops: int = -1, fade_in_ms: int = 0)` | `None` | Play background music. `loops`: -1 = loop forever, 0 = play once. `fade_in_ms`: fade-in duration in milliseconds (0 = instant). |
| `stop` | `(fade_out_ms: int = 0)` | `None` | Stop music. `fade_out_ms`: fade-out duration in milliseconds (0 = instant halt). |
| `pause` | `()` | `None` | Pause music playback. |
| `resume` | `()` | `None` | Resume paused music. |
| `set_volume` | `(volume: float)` | `None` | Set music volume: 0.0 to 1.0. |
| `is_playing` | `()` | `bool` | `True` if music is playing and NOT paused. |
| `is_paused` | `()` | `bool` | `True` if music is paused. |

### Usage

```python
class GameScene(Scene):
    def on_enter(self):
        Music.play("music/bgm.mp3", volume=0.6, fade_in_ms=1000)

    def on_exit(self):
        Music.stop(fade_out_ms=500)
```
