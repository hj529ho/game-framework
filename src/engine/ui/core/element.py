from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from engine.math.vector2 import Vector2
from engine.math.rect import Rect
from engine.ui.core.style import Style
from engine.ui.events import UIEvent

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer


class Element:
    """Base UI element. DOM Node equivalent.

    Maintains a tree of children, handles event bubbling,
    and provides layout/render interface.

    Style can be a Style object, a CSS string, or both:
        Element(style="width: 200px; height: 100px")
        Element(style=Style(width=px(200)))
    """

    _next_id: int = 0

    def __init__(self, style: Style | str | None = None, id: str = "",
                 class_name: str = "") -> None:
        Element._next_id += 1
        self._uid = Element._next_id
        self.id = id
        self.class_name = class_name  # CSS class names (space-separated)

        if isinstance(style, str):
            self.style = Style(style)
        elif style is not None:
            self.style = style
        else:
            self.style = Style()

        self._parent: Element | None = None
        self._children: list[Element] = []

        # Computed layout (set by layout engine)
        self._computed_x: float = 0.0
        self._computed_y: float = 0.0
        self._computed_w: float = 0.0
        self._computed_h: float = 0.0

        # Event handlers: event_type_name -> list of callbacks
        self._handlers: dict[str, list[Callable[[UIEvent], None]]] = {}

        # State
        self._hovered: bool = False
        self._focused: bool = False
        self._visible: bool = True
        self._dirty: bool = True

    # --- Tree ---

    @property
    def parent(self) -> Element | None:
        return self._parent

    @property
    def children(self) -> list[Element]:
        return self._children.copy()

    def append(self, child: Element) -> Element:
        """Add a child element at the end."""
        if child._parent is not None:
            child._parent.remove(child)
        child._parent = self
        self._children.append(child)
        self._mark_dirty()
        return child

    def prepend(self, child: Element) -> Element:
        """Add a child element at the beginning."""
        if child._parent is not None:
            child._parent.remove(child)
        child._parent = self
        self._children.insert(0, child)
        self._mark_dirty()
        return child

    def remove(self, child: Element) -> None:
        """Remove a child element."""
        if child in self._children:
            self._children.remove(child)
            child._parent = None
            self._mark_dirty()

    def remove_all(self) -> None:
        """Remove all children."""
        for c in self._children:
            c._parent = None
        self._children.clear()
        self._mark_dirty()

    # --- Query ---

    def find_by_id(self, id: str) -> Element | None:
        """Find descendant by id (depth-first)."""
        if self.id == id:
            return self
        for child in self._children:
            found = child.find_by_id(id)
            if found:
                return found
        return None

    def find_all_by_type(self, elem_type: type) -> list[Element]:
        """Find all descendants of a given type."""
        result = []
        if isinstance(self, elem_type):
            result.append(self)
        for child in self._children:
            result.extend(child.find_all_by_type(elem_type))
        return result

    # --- Computed layout (read by renderer, written by layout engine) ---

    @property
    def computed_rect(self) -> Rect:
        return Rect(self._computed_x, self._computed_y,
                     self._computed_w, self._computed_h)

    @property
    def absolute_rect(self) -> Rect:
        """Rect in screen space (accumulated from parents)."""
        x, y = self._computed_x, self._computed_y
        p = self._parent
        while p is not None:
            x += p._computed_x + p.style.padding.left + p.style.border_width
            y += p._computed_y + p.style.padding.top + p.style.border_width
            p = p._parent
        return Rect(x, y, self._computed_w, self._computed_h)

    # --- Events ---

    def on(self, event_name: str, handler: Callable[[UIEvent], None]) -> None:
        """Subscribe to an event (e.g. 'click', 'hover', 'focus')."""
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)

    def off(self, event_name: str, handler: Callable | None = None) -> None:
        """Unsubscribe. If handler is None, remove all for that event."""
        if handler is None:
            self._handlers.pop(event_name, None)
        elif event_name in self._handlers:
            self._handlers[event_name] = [
                h for h in self._handlers[event_name] if h is not handler
            ]

    def emit(self, event_name: str, event: UIEvent) -> None:
        """Emit an event with bubbling (child -> parent)."""
        event.target = event.target or self
        event.current_target = self

        for handler in self._handlers.get(event_name, []):
            handler(event)
            if event.propagation_stopped:
                return

        # Bubble to parent
        if self._parent and not event.propagation_stopped:
            self._parent.emit(event_name, event)

    # --- Hit test ---

    def hit_test(self, x: float, y: float) -> Element | None:
        """Find the deepest element at screen position (x, y).
        Children are tested in reverse order (last = top = checked first).
        """
        if not self._visible or self.style.display == "none":
            return None

        rect = self.absolute_rect

        if not rect.contains_point(Vector2(x, y)):
            return None

        # Check children in reverse (topmost first)
        for child in reversed(self._children):
            hit = child.hit_test(x, y)
            if hit:
                return hit

        return self

    # --- State ---

    @property
    def hovered(self) -> bool:
        return self._hovered

    @property
    def focused(self) -> bool:
        return self._focused

    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._visible = value
        self._mark_dirty()

    # --- Dirty tracking ---

    def _mark_dirty(self) -> None:
        self._dirty = True
        if self._parent:
            self._parent._mark_dirty()

    # --- Render (overridden by subclasses) ---

    def draw(self, renderer: Renderer, offset_x: float = 0, offset_y: float = 0) -> None:
        """Draw this element and its children. Override in subclasses."""
        if not self._visible or self.style.display == "none":
            return

        self._draw_self(renderer, offset_x, offset_y)
        self._draw_children(renderer, offset_x, offset_y)

    def _draw_self(self, renderer: Renderer, ox: float, oy: float) -> None:
        """Draw this element's box (background, border). Override for custom rendering."""
        pass

    def _draw_children(self, renderer: Renderer, ox: float, oy: float) -> None:
        px_off = self._computed_x + ox + self.style.padding.left + self.style.border_width
        py_off = self._computed_y + oy + self.style.padding.top + self.style.border_width
        for child in self._children:
            child.draw(renderer, px_off, py_off)

    def __repr__(self) -> str:
        name = type(self).__name__
        id_str = f" id='{self.id}'" if self.id else ""
        return f"<{name}{id_str} {self._computed_w:.0f}x{self._computed_h:.0f}>"
