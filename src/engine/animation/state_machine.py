from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any

from engine.animation.clip import AnimationClip


@dataclass
class AnimationTransition:
    """Defines a transition rule between two states.

    Attributes:
        from_state: Source state name. "*" means any state.
        to_state: Target state name.
        condition: Callable that takes the parameter dict and returns bool.
        exit_time: If set (0.0~1.0), transition only triggers after this
                   fraction of the current clip has played. None = immediate.
        has_exit_time: If True, waits for exit_time before transitioning.
    """
    from_state: str
    to_state: str
    condition: Callable[[dict[str, Any]], bool] | None = None
    exit_time: float | None = None

    @property
    def has_exit_time(self) -> bool:
        return self.exit_time is not None


class AnimationState:
    """A single state in the state machine, wrapping an AnimationClip."""

    def __init__(self, name: str, clip: AnimationClip) -> None:
        self.name = name
        self.clip = clip
        self._frame_index: int = 0
        self._timer: float = 0.0
        self._finished: bool = False
        self._events_fired: set[int] = set()

    @property
    def current_frame(self) -> int:
        if self.clip.frames:
            return self.clip.frames[self._frame_index]
        return 0

    @property
    def frame_index(self) -> int:
        return self._frame_index

    @property
    def normalized_time(self) -> float:
        """0.0 ~ 1.0 progress through the clip."""
        if not self.clip.frames:
            return 1.0
        return self._frame_index / max(1, len(self.clip.frames) - 1)

    @property
    def is_finished(self) -> bool:
        return self._finished

    def reset(self) -> None:
        self._frame_index = 0
        self._timer = 0.0
        self._finished = False
        self._events_fired.clear()

    def update(self, dt: float) -> None:
        if self._finished or not self.clip.frames:
            return

        self._timer += dt
        frame_duration = 1.0 / self.clip.fps if self.clip.fps > 0 else 0

        while self._timer >= frame_duration and frame_duration > 0:
            self._timer -= frame_duration

            # Fire events for current frame
            self._fire_events()

            self._frame_index += 1
            if self._frame_index >= len(self.clip.frames):
                if self.clip.loop:
                    self._frame_index = 0
                    self._events_fired.clear()
                else:
                    self._frame_index = len(self.clip.frames) - 1
                    self._finished = True
                    self._fire_events()
                    break

    def _fire_events(self) -> None:
        for event in self.clip.events:
            if event.frame == self._frame_index and event.frame not in self._events_fired:
                self._events_fired.add(event.frame)
                event.callback()


class AnimatorStateMachine:
    """Unity-style animation state machine.

    Define states (each wrapping an AnimationClip), transitions between them,
    and parameters that drive transition conditions.

    Example:
        asm = AnimatorStateMachine()

        # Add states
        asm.add_state("idle", AnimationClip("idle", [0,1,2,3], fps=8))
        asm.add_state("run", AnimationClip("run", [4,5,6,7,8,9], fps=12))
        asm.add_state("attack", AnimationClip("attack", [10,11,12,13], fps=15, loop=False))

        # Add parameters
        asm.set_param("speed", 0.0)
        asm.set_param("attacking", False)

        # Add transitions
        asm.add_transition("idle", "run", condition=lambda p: p["speed"] > 0.1)
        asm.add_transition("run", "idle", condition=lambda p: p["speed"] <= 0.1)
        asm.add_transition("*", "attack", condition=lambda p: p["attacking"])
        asm.add_transition("attack", "idle", exit_time=1.0)  # after clip finishes

        # Set initial state
        asm.play("idle")
    """

    def __init__(self) -> None:
        self._states: dict[str, AnimationState] = {}
        self._transitions: list[AnimationTransition] = []
        self._params: dict[str, Any] = {}
        self._current: AnimationState | None = None
        self._on_state_enter: Callable[[str, str], None] | None = None
        self._on_state_exit: Callable[[str], None] | None = None

    # --- State management ---

    def add_state(self, name: str, clip: AnimationClip) -> None:
        self._states[name] = AnimationState(name, clip)

    def play(self, name: str) -> None:
        """Force-switch to a state, resetting it."""
        state = self._states.get(name)
        if state is None:
            raise ValueError(f"State '{name}' not found.")

        old_name = self._current.name if self._current else ""
        if self._current and self._on_state_exit:
            self._on_state_exit(old_name)

        state.reset()
        self._current = state

        if self._on_state_enter:
            self._on_state_enter(old_name, name)

    @property
    def current_state(self) -> str:
        return self._current.name if self._current else ""

    @property
    def current_frame(self) -> int:
        return self._current.current_frame if self._current else 0

    @property
    def is_finished(self) -> bool:
        return self._current.is_finished if self._current else True

    @property
    def normalized_time(self) -> float:
        return self._current.normalized_time if self._current else 1.0

    # --- Parameters ---

    def set_param(self, name: str, value: Any) -> None:
        self._params[name] = value

    def get_param(self, name: str) -> Any:
        return self._params.get(name)

    # --- Transitions ---

    def add_transition(
        self,
        from_state: str,
        to_state: str,
        condition: Callable[[dict[str, Any]], bool] | None = None,
        exit_time: float | None = None,
    ) -> None:
        """Add a transition rule.

        Args:
            from_state: Source state name. Use "*" for any state.
            to_state: Target state name.
            condition: Callable(params) -> bool. If None, only exit_time is checked.
            exit_time: 0.0~1.0. Transition fires after this fraction of the clip.
                       None = check condition every frame (no exit time requirement).
        """
        self._transitions.append(AnimationTransition(
            from_state=from_state,
            to_state=to_state,
            condition=condition,
            exit_time=exit_time,
        ))

    # --- Callbacks ---

    def on_state_enter(self, callback: Callable[[str, str], None]) -> None:
        """Register callback(old_state, new_state) on state enter."""
        self._on_state_enter = callback

    def on_state_exit(self, callback: Callable[[str], None]) -> None:
        """Register callback(old_state) on state exit."""
        self._on_state_exit = callback

    # --- Update ---

    def update(self, dt: float) -> None:
        if self._current is None:
            return

        self._current.update(dt)
        self._check_transitions()

    def _check_transitions(self) -> None:
        if self._current is None:
            return

        current_name = self._current.name

        for t in self._transitions:
            # Match from_state
            if t.from_state != "*" and t.from_state != current_name:
                continue

            # Don't transition to self (unless from "*")
            if t.to_state == current_name and t.from_state != "*":
                continue

            # Check exit_time
            if t.has_exit_time:
                if self._current.normalized_time < t.exit_time:
                    continue

            # Check condition
            if t.condition is not None:
                if not t.condition(self._params):
                    continue

            # All checks passed — transition
            self.play(t.to_state)
            break
