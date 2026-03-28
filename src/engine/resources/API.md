# engine.resources -- API Reference

## Class: `ResourceManager`

**File**: `resource_manager.py`
**Import**: `from engine.resources.resource_manager import ResourceManager`

Loads and caches game assets: images, fonts, sounds, and music.
Created automatically by `App`. Access via `current_app().resources`.

### Constructor

```python
ResourceManager(sdl_renderer: SDL_Renderer, base_path: str = "assets")
```

Created internally by `App`. `base_path` is the root directory for asset resolution.

### Path Resolution

Files are first resolved relative to `base_path` (default `"assets"`). If not found, falls back to CWD-relative path. Paths are encoded to UTF-8 for SDL2.

---

### Image Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `load_image` | `(path: str)` | `SDL_Texture` | Load image and return SDL texture. Cached by path. Raises `FileNotFoundError` on failure. |
| `get_image_size` | `(path: str)` | `tuple[int, int]` | Get `(width, height)` of cached image. Calls `load_image` if not yet cached. |
| `preload_images` | `(*paths: str)` | `None` | Preload multiple images into cache. |
| `unload_image` | `(path: str)` | `None` | Remove image from cache and free SDL texture. |

### Font Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `load_font` | `(path: str \| None, size: int)` | `TTF_Font` | Load TTF font at given size. Cached by `(path, size)`. Raises `ValueError` if path is `None`. Raises `FileNotFoundError` on failure. |

### Sound Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `load_sound` | `(path: str)` | `Mix_Chunk` | Load short sound effect (WAV/OGG). Cached by path. Raises `FileNotFoundError` on failure. |
| `unload_sound` | `(path: str)` | `None` | Remove sound from cache and free memory. |

### Music Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `load_music` | `(path: str)` | `Mix_Music` | Load streaming music (MP3/OGG). Cached by path. Raises `FileNotFoundError` on failure. |
| `unload_music` | `(path: str)` | `None` | Remove music from cache and free memory. |

### Lifecycle Methods

| Method | Signature | Description |
|---|---|---|
| `clear` | `() -> None` | Unload all cached resources (textures, fonts, sounds, music). |
| `destroy` | `() -> None` | Clear all resources and shut down SDL_image (`IMG_Quit`), SDL_ttf (`TTF_Quit`), SDL_mixer (`Mix_CloseAudio`, `Mix_Quit`). |

### Usage

```python
# Accessed via current_app
resources = current_app().resources
texture = resources.load_image("player.png")
w, h = resources.get_image_size("player.png")
font = resources.load_font("fonts/arial.ttf", 24)
resources.preload_images("bg.png", "enemy.png", "bullet.png")
```
