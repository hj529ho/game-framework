from __future__ import annotations

import ctypes
import os
from pathlib import Path
from typing import TYPE_CHECKING

from sdl2 import (
    SDL_Surface, SDL_Texture, SDL_FreeSurface,
    SDL_CreateTextureFromSurface, SDL_DestroyTexture,
    SDL_QueryTexture,
)
from sdl2.sdlimage import IMG_Load, IMG_Init, IMG_Quit, IMG_INIT_PNG, IMG_INIT_JPG
from sdl2.sdlttf import (
    TTF_Init, TTF_Quit, TTF_OpenFont, TTF_CloseFont, TTF_Font,
)
from sdl2.sdlmixer import (
    Mix_Init, Mix_Quit, Mix_OpenAudio, Mix_CloseAudio,
    Mix_LoadWAV, Mix_LoadMUS, Mix_FreeChunk, Mix_FreeMusic,
    Mix_Chunk, Mix_Music,
    MIX_INIT_MP3, MIX_INIT_OGG, MIX_DEFAULT_FORMAT,
)

if TYPE_CHECKING:
    from sdl2 import SDL_Renderer


class ResourceManager:
    """Loads and caches game assets: images, fonts, sounds, music.

    Usage:
        resources = ResourceManager(renderer, base_path="assets")
        texture = resources.load_image("player.png")
        font = resources.load_font("arial.ttf", 24)
        sound = resources.load_sound("jump.wav")
        music = resources.load_music("bgm.mp3")
    """

    def __init__(self, sdl_renderer: SDL_Renderer, base_path: str = "assets") -> None:
        self._renderer = sdl_renderer
        self._base_path = Path(base_path)

        self._textures: dict[str, SDL_Texture] = {}
        self._texture_sizes: dict[str, tuple[int, int]] = {}
        self._fonts: dict[tuple[str, int], TTF_Font] = {}
        self._sounds: dict[str, Mix_Chunk] = {}
        self._music_cache: dict[str, Mix_Music] = {}

        # Init SDL subsystems
        IMG_Init(IMG_INIT_PNG | IMG_INIT_JPG)
        TTF_Init()
        Mix_Init(MIX_INIT_MP3 | MIX_INIT_OGG)
        Mix_OpenAudio(44100, MIX_DEFAULT_FORMAT, 2, 2048)

    def _resolve_path(self, path: str) -> bytes:
        full = self._base_path / path
        if not full.exists():
            # Try relative to CWD
            full = Path(path)
        return str(full).encode('utf-8')

    # --- Images ---

    def load_image(self, path: str) -> SDL_Texture:
        """Load an image and return an SDL_Texture. Cached by path."""
        if path in self._textures:
            return self._textures[path]

        resolved = self._resolve_path(path)
        surface = IMG_Load(resolved)
        if not surface:
            from sdl2.sdlimage import IMG_GetError
            raise FileNotFoundError(f"Failed to load image '{path}': {IMG_GetError()}")

        texture = SDL_CreateTextureFromSurface(self._renderer, surface)
        SDL_FreeSurface(surface)

        if not texture:
            from sdl2 import SDL_GetError
            raise RuntimeError(f"Failed to create texture: {SDL_GetError()}")

        # Cache size
        w, h = ctypes.c_int(), ctypes.c_int()
        SDL_QueryTexture(texture, None, None, ctypes.byref(w), ctypes.byref(h))
        self._texture_sizes[path] = (w.value, h.value)

        self._textures[path] = texture
        return texture

    def get_image_size(self, path: str) -> tuple[int, int]:
        """Get cached image dimensions. Must call load_image first."""
        if path not in self._texture_sizes:
            self.load_image(path)
        return self._texture_sizes[path]

    # --- Fonts ---

    def load_font(self, path: str | None, size: int) -> TTF_Font:
        """Load a TTF font at given size. None path uses a default.
        Cached by (path, size).
        """
        key = (path or "__default__", size)
        if key in self._fonts:
            return self._fonts[key]

        if path is None:
            raise ValueError("No default font available. Provide a font path.")

        resolved = self._resolve_path(path)
        font = TTF_OpenFont(resolved, size)
        if not font:
            from sdl2.sdlttf import TTF_GetError
            raise FileNotFoundError(f"Failed to load font '{path}': {TTF_GetError()}")

        self._fonts[key] = font
        return font

    # --- Sounds ---

    def load_sound(self, path: str) -> Mix_Chunk:
        """Load a short sound effect (WAV/OGG). Cached by path."""
        if path in self._sounds:
            return self._sounds[path]

        resolved = self._resolve_path(path)
        chunk = Mix_LoadWAV(resolved)
        if not chunk:
            from sdl2.sdlmixer import Mix_GetError
            raise FileNotFoundError(f"Failed to load sound '{path}': {Mix_GetError()}")

        self._sounds[path] = chunk
        return chunk

    # --- Music ---

    def load_music(self, path: str) -> Mix_Music:
        """Load streaming music (MP3/OGG). Cached by path."""
        if path in self._music_cache:
            return self._music_cache[path]

        resolved = self._resolve_path(path)
        music = Mix_LoadMUS(resolved)
        if not music:
            from sdl2.sdlmixer import Mix_GetError
            raise FileNotFoundError(f"Failed to load music '{path}': {Mix_GetError()}")

        self._music_cache[path] = music
        return music

    # --- Preload / Unload ---

    def preload_images(self, *paths: str) -> None:
        for p in paths:
            self.load_image(p)

    def unload_image(self, path: str) -> None:
        tex = self._textures.pop(path, None)
        if tex:
            SDL_DestroyTexture(tex)
        self._texture_sizes.pop(path, None)

    def unload_sound(self, path: str) -> None:
        chunk = self._sounds.pop(path, None)
        if chunk:
            Mix_FreeChunk(chunk)

    def unload_music(self, path: str) -> None:
        mus = self._music_cache.pop(path, None)
        if mus:
            Mix_FreeMusic(mus)

    def clear(self) -> None:
        """Unload all cached resources."""
        for tex in self._textures.values():
            SDL_DestroyTexture(tex)
        self._textures.clear()
        self._texture_sizes.clear()

        for font in self._fonts.values():
            TTF_CloseFont(font)
        self._fonts.clear()

        for chunk in self._sounds.values():
            Mix_FreeChunk(chunk)
        self._sounds.clear()

        for mus in self._music_cache.values():
            Mix_FreeMusic(mus)
        self._music_cache.clear()

    def destroy(self) -> None:
        """Clear all resources and shut down subsystems."""
        self.clear()
        Mix_CloseAudio()
        Mix_Quit()
        TTF_Quit()
        IMG_Quit()
