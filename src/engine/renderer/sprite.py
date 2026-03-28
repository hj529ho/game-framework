from __future__ import annotations

from typing import TYPE_CHECKING

from engine.ecs.component import Component
from engine.math.vector2 import Vector2

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer


class SpriteRenderer(Component):
    """Component that renders an image at the entity's position.

    Example:
        player = Entity("Player")
        sprite = player.add_component(SpriteRenderer())
        sprite.image = "player.png"
        sprite.anchor = Vector2(0.5, 0.5)  # center
    """

    def __init__(self, image: str = "", layer: int = 0) -> None:
        super().__init__()
        self._image_path = image
        self._texture = None
        self._width: int = 0
        self._height: int = 0
        self.layer = layer
        self.anchor = Vector2(0.5, 0.5)  # 0,0=top-left, 0.5,0.5=center
        self.flip_x = False
        self.flip_y = False

    @property
    def image(self) -> str:
        return self._image_path

    @image.setter
    def image(self, path: str) -> None:
        self._image_path = path
        self._texture = None  # will reload on next draw

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def _ensure_loaded(self) -> None:
        if self._texture is None and self._image_path:
            from engine.core.app import current_app
            res = current_app().resources
            self._texture = res.load_image(self._image_path)
            self._width, self._height = res.get_image_size(self._image_path)

    def on_draw(self, renderer: Renderer) -> None:
        if not self._image_path:
            return
        self._ensure_loaded()
        if self._texture is None:
            return

        pos = self.position
        scale = self.entity.scale
        w = int(self._width * scale.x)
        h = int(self._height * scale.y)
        x = pos.x - w * self.anchor.x
        y = pos.y - h * self.anchor.y

        renderer.draw_texture(
            self._texture,
            x, y,
            width=w, height=h,
            angle=self.entity.rotation,
            layer=self.layer,
        )
