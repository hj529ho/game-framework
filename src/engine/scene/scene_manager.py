from __future__ import annotations

from typing import TYPE_CHECKING

from engine.scene.scene import Scene

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer
    from engine.scene.transition import Transition


class SceneManager:
    """Stack-based scene manager with optional transitions."""

    def __init__(self) -> None:
        self._stack: list[Scene] = []
        self._pending: list[tuple[str, Scene | None, Transition | None]] = []
        self._transition: Transition | None = None
        self._transition_action: str = ""
        self._transition_scene: Scene | None = None
        self._transition_midpoint_done: bool = False

    @property
    def current(self) -> Scene | None:
        return self._stack[-1] if self._stack else None

    @property
    def stack_depth(self) -> int:
        return len(self._stack)

    @property
    def transitioning(self) -> bool:
        return self._transition is not None

    def push(self, scene: Scene, transition: Transition | None = None) -> None:
        self._pending.append(("push", scene, transition))

    def pop(self, transition: Transition | None = None) -> None:
        self._pending.append(("pop", None, transition))

    def replace(self, scene: Scene, transition: Transition | None = None) -> None:
        self._pending.append(("replace", scene, transition))

    def clear(self) -> None:
        self._pending.append(("clear", None, None))

    def process_pending(self) -> None:
        # Don't process if a transition is running
        if self._transition is not None:
            return

        for action, scene, transition in self._pending:
            if transition is not None:
                # Start transition — defer the actual scene change to midpoint
                self._transition = transition
                self._transition_action = action
                self._transition_scene = scene
                self._transition_midpoint_done = False
                break  # only start one transition at a time
            else:
                self._execute_action(action, scene)

        self._pending.clear()

    def _execute_action(self, action: str, scene: Scene | None) -> None:
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

    def update(self, dt: float) -> None:
        # Update transition
        if self._transition is not None:
            self._transition.update(dt)

            # At midpoint, execute the scene change
            midpoint = getattr(self._transition, 'at_midpoint', None)
            if midpoint and not self._transition_midpoint_done:
                self._execute_action(self._transition_action, self._transition_scene)
                self._transition_midpoint_done = True

            # Transition complete
            if self._transition.is_complete:
                if not self._transition_midpoint_done:
                    self._execute_action(self._transition_action, self._transition_scene)
                self._transition = None
                self._transition_scene = None

        # Update current scene
        if self._stack:
            self._stack[-1].update(dt)

        # Process pending (only if no transition running)
        if self._transition is None:
            self.process_pending()

    def draw(self, renderer: Renderer) -> None:
        if self._stack:
            self._stack[-1].draw(renderer)

        # Draw transition overlay
        if self._transition is not None:
            self._transition.draw(renderer)
