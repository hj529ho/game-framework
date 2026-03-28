from __future__ import annotations

from typing import TypeVar, TYPE_CHECKING

from engine.ecs.entity import Entity
from engine.ecs.component import Component
from engine.ecs.world import World
from engine.ui.core.element import Element
from engine.ui.core.layout import compute_layout

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer

T = TypeVar("T", bound=Component)


class Scene:
    """Game scene. Owns a World of entities and a HUD UI tree.

    Three render layers:
        1. Game World  -- entities with components (camera-affected)
        2. In-Game UI  -- per-entity UI (camera-affected, via entity.game_ui)
        3. HUD         -- screen-fixed UI (no camera, via scene.hud)

    Example:
        class GameScene(Scene):
            def on_enter(self):
                player = Entity("Player")
                player.add_component(PlayerMovement())
                self.add(player)

                # HUD (screen-fixed)
                from engine.ui import Div, Text, Style, ProgressBar
                hud_bar = Div(style="display: flex; flex-direction: row; "
                                    "padding: 10px; gap: 10px")
                hud_bar.append(Text("HP:", style="color: red; font-size: 18px"))
                hud_bar.append(ProgressBar(0.8, style="width: 200px; height: 20px; background: #333"))
                self.hud.append(hud_bar)
    """

    def __init__(self, name: str = "") -> None:
        self._name = name or type(self).__name__
        self._world = World()
        self._hud = Element()  # HUD root (screen-space UI)
        self._hud_dirty = True
        self._hud_width: int = 800
        self._hud_height: int = 600

    @property
    def name(self) -> str:
        return self._name

    @property
    def world(self) -> World:
        return self._world

    @property
    def hud(self) -> Element:
        """HUD root element. Append UI elements here for screen-fixed UI."""
        return self._hud

    # --- Entity convenience ---

    def add(self, entity: Entity) -> Entity:
        return self._world.add(entity)

    def remove(self, entity: Entity) -> None:
        self._world.remove(entity)

    def find(self, name: str) -> Entity | None:
        return self._world.find_by_name(name)

    def find_by_tag(self, tag: str) -> list[Entity]:
        return self._world.find_by_tag(tag)

    def find_with_component(self, *comp_types: type[T]) -> list[Entity]:
        return self._world.find_with_component(*comp_types)

    # --- Scene lifecycle hooks (override in subclass) ---

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def on_pause(self) -> None:
        pass

    def on_resume(self) -> None:
        pass

    # --- Frame methods (called by SceneManager) ---

    def update(self, dt: float) -> None:
        self._world.update(dt)

        # Resolve HUD viewport size
        try:
            from engine.core.app import current_app
            app = current_app()
            self._hud_width = app.width
            self._hud_height = app.height
        except RuntimeError:
            pass

    def draw(self, renderer: Renderer) -> None:
        # Layer 1: Game World (camera-affected, handled by component on_draw)
        self._world.draw(renderer)

        # Layer 2: In-Game UI (camera-affected, per-entity)
        for entity in self._world.entities:
            if entity.active and entity._game_ui_root is not None:
                self._draw_entity_ui(entity, renderer)

        # Layer 3: HUD (screen-fixed, no camera)
        if self._hud._children:
            if self._hud._dirty or self._hud_dirty:
                compute_layout(self._hud, self._hud_width, self._hud_height)
                self._hud._dirty = False
                self._hud_dirty = False
            self._hud.draw(renderer)

    def _draw_entity_ui(self, entity: Entity, renderer: Renderer) -> None:
        """Draw an entity's in-game UI at its screen position."""
        from engine.renderer.camera import Camera2D
        cam = Camera2D.get_active()

        ui_root = entity._game_ui_root
        if not ui_root._children:
            return

        # Compute layout once
        if ui_root._dirty:
            compute_layout(ui_root, 200, 100)  # reasonable default for floating UI
            ui_root._dirty = False

        # Get entity's screen position
        pos = entity.position
        if cam:
            screen_pos = cam.world_to_screen(pos)
        else:
            screen_pos = pos

        # Center UI above entity
        total_w = ui_root._computed_w
        total_h = ui_root._computed_h
        offset_x = screen_pos.x - total_w / 2
        offset_y = screen_pos.y - total_h - 10  # 10px above entity

        ui_root._computed_x = offset_x
        ui_root._computed_y = offset_y
        ui_root.draw(renderer)
