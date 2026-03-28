from __future__ import annotations

import ctypes
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sdl2 import (
    SDL_Rect, SDL_CreateTextureFromSurface, SDL_FreeSurface,
    SDL_QueryTexture, SDL_Texture,
)

from engine.ecs.component import Component
from engine.math.vector2 import Vector2

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer


@dataclass
class Animation:
    """Defines a named animation from a spritesheet."""
    frames: list[int]          # frame indices in the spritesheet
    fps: float = 10.0          # playback speed
    loop: bool = True          # loop when finished


class AnimatedSprite(Component):
    """Component that plays spritesheet animations.

    The spritesheet is a single image with frames laid out in a grid.

    Example:
        anim = entity.add_component(AnimatedSprite(
            image="player_sheet.png",
            frame_width=32,
            frame_height=32,
        ))
        anim.add_animation("idle", Animation(frames=[0, 1, 2, 3], fps=8))
        anim.add_animation("run", Animation(frames=[4, 5, 6, 7, 8, 9], fps=12))
        anim.play("idle")
    """

    def __init__(
        self,
        image: str = "",
        frame_width: int = 32,
        frame_height: int = 32,
        layer: int = 0,
    ) -> None:
        super().__init__()
        self._image_path = image
        self._frame_w = frame_width
        self._frame_h = frame_height
        self.layer = layer
        self.anchor = Vector2(0.5, 0.5)

        self._texture: SDL_Texture | None = None
        self._sheet_cols: int = 1
        self._sheet_rows: int = 1

        self._animations: dict[str, Animation] = {}
        self._current_name: str = ""
        self._current_anim: Animation | None = None
        self._frame_index: int = 0
        self._timer: float = 0.0
        self._playing: bool = False
        self._finished: bool = False

    @property
    def image(self) -> str:
        return self._image_path

    @image.setter
    def image(self, path: str) -> None:
        self._image_path = path
        self._texture = None

    @property
    def frame_width(self) -> int:
        return self._frame_w

    @property
    def frame_height(self) -> int:
        return self._frame_h

    @property
    def current_animation(self) -> str:
        return self._current_name

    @property
    def is_playing(self) -> bool:
        return self._playing

    @property
    def is_finished(self) -> bool:
        return self._finished

    @property
    def current_frame(self) -> int:
        if self._current_anim and self._current_anim.frames:
            return self._current_anim.frames[self._frame_index]
        return 0

    def add_animation(self, name: str, animation: Animation) -> None:
        self._animations[name] = animation

    def play(self, name: str, restart: bool = False) -> None:
        """Play an animation by name. If already playing, does nothing unless restart=True."""
        if name == self._current_name and self._playing and not restart:
            return
        anim = self._animations.get(name)
        if anim is None:
            raise ValueError(f"Animation '{name}' not found.")
        self._current_name = name
        self._current_anim = anim
        self._frame_index = 0
        self._timer = 0.0
        self._playing = True
        self._finished = False

    def stop(self) -> None:
        self._playing = False

    def _ensure_loaded(self) -> None:
        if self._texture is None and self._image_path:
            from engine.core.app import current_app
            res = current_app().resources
            self._texture = res.load_image(self._image_path)
            w, h = res.get_image_size(self._image_path)
            self._sheet_cols = max(1, w // self._frame_w)
            self._sheet_rows = max(1, h // self._frame_h)

    def on_update(self, dt: float) -> None:
        if not self._playing or self._current_anim is None:
            return

        anim = self._current_anim
        if not anim.frames:
            return

        self._timer += dt
        frame_duration = 1.0 / anim.fps

        while self._timer >= frame_duration:
            self._timer -= frame_duration
            self._frame_index += 1

            if self._frame_index >= len(anim.frames):
                if anim.loop:
                    self._frame_index = 0
                else:
                    self._frame_index = len(anim.frames) - 1
                    self._playing = False
                    self._finished = True
                    break

    def on_draw(self, renderer: Renderer) -> None:
        if not self._image_path:
            return
        self._ensure_loaded()
        if self._texture is None:
            return

        frame = self.current_frame
        col = frame % self._sheet_cols
        row = frame // self._sheet_cols

        src = SDL_Rect(
            col * self._frame_w, row * self._frame_h,
            self._frame_w, self._frame_h,
        )

        pos = self.position
        scale = self.entity.scale
        w = int(self._frame_w * scale.x)
        h = int(self._frame_h * scale.y)
        x = pos.x - w * self.anchor.x
        y = pos.y - h * self.anchor.y

        # Use world_space draw with source rect
        from engine.renderer.camera import Camera2D
        cam = Camera2D.get_active()
        if cam:
            sp = cam.world_to_screen(Vector2(x, y))
            zoom = cam.zoom
            dst = SDL_Rect(int(sp.x), int(sp.y), int(w * zoom), int(h * zoom))
        else:
            dst = SDL_Rect(int(x), int(y), w, h)

        from sdl2 import SDL_RenderCopy, SDL_RenderCopyEx
        angle = self.entity.rotation
        sdl_r = renderer.sdl_renderer

        if angle == 0.0:
            def _draw():
                SDL_RenderCopy(sdl_r, self._texture, src, dst)
        else:
            def _draw():
                SDL_RenderCopyEx(sdl_r, self._texture, src, dst, angle, None, 0)

        renderer._enqueue(self.layer, _draw)
