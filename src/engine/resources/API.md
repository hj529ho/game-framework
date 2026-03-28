# engine.resources -- API Reference

## Class: `ResourceManager`

**File**: `resource_manager.py`
**Import**: `from engine.resources import ResourceManager`

Loads and caches game assets (images, fonts, sounds, music).
Created automatically by `App`. Access via `current_app().resources`.

### Constructor

```python
ResourceManager(sdl_renderer: SDL_Renderer, base_path: str = "assets")
```

Created internally by App. `base_path` is the root directory for asset resolution.

### Image Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `load_image` | `(path: str)` | `SDL_Texture` | Load and cache image. Returns SDL texture. |
| `get_image_size` | `(path: str)` | `tuple[int, int]` | Get (width, height) of cached image. |
| `preload_images` | `(*paths: str)` | `None` | Preload multiple images into cache. |
| `unload_image` | `(path: str)` | `None` | Remove image from cache, free texture. |

### Font Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `load_font` | `(path: str \| None, size: int)` | `TTF_Font` | Load TTF font at given size. Cached by (path, size). |

### Sound Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `load_sound` | `(path: str)` | `Mix_Chunk` | Load short sound effect (WAV/OGG). |
| `unload_sound` | `(path: str)` | `None` | Free cached sound. |

### Music Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `load_music` | `(path: str)` | `Mix_Music` | Load streaming music (MP3/OGG). |
| `unload_music` | `(path: str)` | `None` | Free cached music. |

### Lifecycle

| Method | Signature | Description |
|---|---|---|
| `clear` | `()` | Unload all cached resources. |
| `destroy` | `()` | Clear + shut down SDL_image, SDL_ttf, SDL_mixer. |

### Path Resolution

Files are resolved relative to `base_path` (default "assets"). If not found there, falls back to CWD-relative path.
