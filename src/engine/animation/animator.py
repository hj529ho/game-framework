from __future__ import annotations

import ctypes
from typing import Any, Callable, TYPE_CHECKING

from sdl2 import SDL_Rect

from engine.ecs.component import Component
from engine.math.vector2 import Vector2
from engine.animation.clip import AnimationClip
from engine.animation.state_machine import AnimatorStateMachine

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer
    from sdl2 import SDL_Texture


class Animator(Component):
    """Component that drives spritesheet animation via a state machine.

    Combines AnimatorStateMachine with spritesheet rendering.
    Attach to an Entity to animate it.

    Example:
        animator = entity.add_component(Animator(
            image="player.png",
            frame_width=32,
            frame_height=32,
        ))

        # Define clips
        idle = AnimationClip("idle", [0,1,2,3], fps=8)
        run = AnimationClip("run", [4,5,6,7,8,9], fps=12)
        attack = AnimationClip("attack", [10,11,12,13], fps=15, loop=False)
        attack.add_event(2, lambda: print("Slash!"))

        # Setup state machine
        animator.add_state("idle", idle)
        animator.add_state("run", run)
        animator.add_state("attack", attack)

        animator.add_transition("idle", "run", condition=lambda p: p["speed"] > 0.1)
        animator.add_transition("run", "idle", condition=lambda p: p["speed"] <= 0.1)
        animator.add_transition("*", "attack", condition=lambda p: p["attacking"])
        animator.add_transition("attack", "idle", exit_time=1.0)

        animator.play("idle")
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
        self.flip_x = False
        self.flip_y = False

        self._texture: SDL_Texture | None = None
        self._sheet_cols: int = 1

        self._sm = AnimatorStateMachine()

    # --- State machine delegation ---

    @property
    def state_machine(self) -> AnimatorStateMachine:
        return self._sm

    @property
    def current_state(self) -> str:
        return self._sm.current_state

    @property
    def current_frame(self) -> int:
        return self._sm.current_frame

    def add_state(self, name: str, clip: AnimationClip) -> None:
        self._sm.add_state(name, clip)

    def add_transition(
        self,
        from_state: str,
        to_state: str,
        condition: Callable[[dict[str, Any]], bool] | None = None,
        exit_time: float | None = None,
    ) -> None:
        self._sm.add_transition(from_state, to_state, condition, exit_time)

    def set_param(self, name: str, value: Any) -> None:
        self._sm.set_param(name, value)

    def get_param(self, name: str) -> Any:
        return self._sm.get_param(name)

    def play(self, name: str) -> None:
        self._sm.play(name)

    # --- Image ---

    @property
    def image(self) -> str:
        return self._image_path

    @image.setter
    def image(self, path: str) -> None:
        self._image_path = path
        self._texture = None

    def _ensure_loaded(self) -> None:
        if self._texture is None and self._image_path:
            from engine.core.app import current_app
            res = current_app().resources
            self._texture = res.load_image(self._image_path)
            w, _ = res.get_image_size(self._image_path)
            self._sheet_cols = max(1, w // self._frame_w)

    # --- Lifecycle ---

    def on_update(self, dt: float) -> None:
        self._sm.update(dt)

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

        from engine.renderer.camera import Camera2D
        cam = Camera2D.get_active()
        if cam:
            sp = cam.world_to_screen(Vector2(x, y))
            zoom = cam.zoom
            dst = SDL_Rect(int(sp.x), int(sp.y), int(w * zoom), int(h * zoom))
        else:
            dst = SDL_Rect(int(x), int(y), w, h)

        from sdl2 import SDL_RenderCopy, SDL_RenderCopyEx, SDL_FLIP_HORIZONTAL, SDL_FLIP_VERTICAL
        sdl_r = renderer.sdl_renderer
        angle = self.entity.rotation
        flip_flag = 0
        if self.flip_x:
            flip_flag |= SDL_FLIP_HORIZONTAL
        if self.flip_y:
            flip_flag |= SDL_FLIP_VERTICAL

        if angle == 0.0 and flip_flag == 0:
            def _draw():
                SDL_RenderCopy(sdl_r, self._texture, src, dst)
        else:
            def _draw():
                SDL_RenderCopyEx(sdl_r, self._texture, src, dst, angle, None, flip_flag)

        renderer._enqueue(self.layer, _draw)
