from __future__ import annotations

from typing import TYPE_CHECKING

from engine.ecs.component import Component
from engine.ui.core.element import Element
from engine.ui.core.layout import compute_layout
from engine.ui.events import ClickEvent, HoverEvent, HoverExitEvent
from engine.input.keys import MouseButton

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer


class UIRoot(Component):
    """Component that owns a UI element tree and drives layout/rendering/events.

    Attach to an Entity to create a UI layer. UIRoot handles:
    - Layout computation (flexbox)
    - Rendering (draws all elements on screen-space, no camera transform)
    - Mouse events (hover, click) with bubbling

    Example:
        ui_entity = Entity("HUD")
        ui = ui_entity.add_component(UIRoot(800, 600))

        panel = Div(style=Style(
            width=px(200), padding=EdgeInsets.all(10),
            background_color=Color(0, 0, 0, 180),
        ))
        panel.append(Text("HP: 100", style=Style(font="f.ttf", font_size=16, color=Color.RED)))
        ui.root.append(panel)
    """

    def __init__(self, width: int = 800, height: int = 600) -> None:
        super().__init__()
        self._width = width
        self._height = height
        self._root = Element()
        self._hovered: Element | None = None
        self._focused: Element | None = None
        self._needs_layout = True

    @property
    def root(self) -> Element:
        """The root element of the UI tree. Append children here."""
        return self._root

    @property
    def focused(self) -> Element | None:
        return self._focused

    def set_focus(self, element: Element | None) -> None:
        from engine.ui.events import FocusEvent, BlurEvent
        if self._focused is not None and self._focused is not element:
            self._focused._focused = False
            self._focused.emit("blur", BlurEvent())
        self._focused = element
        if element is not None:
            element._focused = True
            element.emit("focus", FocusEvent())

    def invalidate(self) -> None:
        """Force layout recalculation next frame."""
        self._needs_layout = True

    def on_update(self, dt: float) -> None:
        app = None
        try:
            from engine.core.app import current_app
            app = current_app()
        except RuntimeError:
            return

        mouse = app.mouse

        # Hit test for hover
        mx, my = mouse.position.x, mouse.position.y
        hit = self._root.hit_test(mx, my)

        if hit != self._hovered:
            if self._hovered is not None:
                self._hovered._hovered = False
                self._hovered.emit("hover_exit", HoverExitEvent())
            self._hovered = hit
            if hit is not None:
                hit._hovered = True
                hit.emit("hover", HoverEvent(x=mx, y=my))

        # Click
        if mouse.is_just_pressed(MouseButton.LEFT) and hit is not None:
            hit.emit("click", ClickEvent(x=mx, y=my, button=1))
            self.set_focus(hit)
        elif mouse.is_just_pressed(MouseButton.RIGHT) and hit is not None:
            hit.emit("click", ClickEvent(x=mx, y=my, button=3))

    def on_draw(self, renderer: Renderer) -> None:
        # Recompute layout if needed
        if self._needs_layout or self._root._dirty:
            compute_layout(self._root, self._width, self._height)
            self._root._dirty = False
            self._needs_layout = False

        # Draw all elements (screen-space, no camera)
        self._root.draw(renderer)
