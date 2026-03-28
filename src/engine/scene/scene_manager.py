from __future__ import annotations

from typing import TYPE_CHECKING

from engine.scene.scene import Scene

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer


class SceneManager:
    """Stack-based scene manager. User calls update/draw from their loop."""

    def __init__(self) -> None:
        self._stack: list[Scene] = []
        self._pending: list[tuple[str, Scene | None]] = []

    @property
    def current(self) -> Scene | None:
        return self._stack[-1] if self._stack else None

    @property
    def stack_depth(self) -> int:
        return len(self._stack)

    def push(self, scene: Scene) -> None:
        """Push a new scene on top. Current scene gets paused."""
        self._pending.append(("push", scene))

    def pop(self) -> None:
        """Pop the top scene. Scene below gets resumed."""
        self._pending.append(("pop", None))

    def replace(self, scene: Scene) -> None:
        """Replace the top scene."""
        self._pending.append(("replace", scene))

    def clear(self) -> None:
        """Remove all scenes."""
        self._pending.append(("clear", None))

    def process_pending(self) -> None:
        """Process queued scene changes. Call once per frame."""
        for action, scene in self._pending:
            if action == "push":
                if self._stack:
                    self._stack[-1].on_pause()
                self._stack.append(scene)
                scene.on_enter()

            elif action == "pop":
                if self._stack:
                    old = self._stack.pop()
                    old.on_exit()
                    if self._stack:
                        self._stack[-1].on_resume()

            elif action == "replace":
                if self._stack:
                    old = self._stack.pop()
                    old.on_exit()
                self._stack.append(scene)
                scene.on_enter()

            elif action == "clear":
                while self._stack:
                    old = self._stack.pop()
                    old.on_exit()

        self._pending.clear()

    def update(self, dt: float) -> None:
        """Update the current (top) scene, then process pending changes."""
        if self._stack:
            self._stack[-1].update(dt)
        self.process_pending()

    def draw(self, renderer: Renderer) -> None:
        """Draw the current (top) scene."""
        if self._stack:
            self._stack[-1].draw(renderer)
