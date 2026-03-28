from __future__ import annotations

from typing import Callable, Any, TypeVar
from enum import Enum, auto

from engine.math.easing import linear, EASINGS
from engine.math.vector2 import Vector2
from engine.renderer.color import Color
from engine.ecs.component import Component


class LoopType(Enum):
    NONE = auto()        # play once
    RESTART = auto()     # restart from beginning
    YOYO = auto()        # ping-pong back and forth


class Tween:
    """A single property animation. DOTween-style API.

    Tweens a value from start to end over duration using an easing function.
    Chain methods for configuration.

    Example:
        # Tween entity position
        Tween.move(entity, Vector2(400, 300), 1.0).set_ease("ease_out_back").play()

        # Tween any property
        Tween.to(lambda: obj.alpha, lambda v: setattr(obj, 'alpha', v), 0.0, 1.0, 0.5).play()
    """

    def __init__(
        self,
        getter: Callable[[], Any],
        setter: Callable[[Any], None],
        start_val: Any,
        end_val: Any,
        duration: float,
    ) -> None:
        self._getter = getter
        self._setter = setter
        self._start = start_val
        self._end = end_val
        self._duration = max(0.001, duration)
        self._elapsed: float = 0.0
        self._ease_fn: Callable[[float], float] = linear
        self._delay: float = 0.0
        self._delay_elapsed: float = 0.0

        self._loop_type = LoopType.NONE
        self._loop_count: int = 0  # 0 = no loop, -1 = infinite
        self._loops_done: int = 0
        self._forward: bool = True

        self._on_complete: Callable[[], None] | None = None
        self._on_update_cb: Callable[[float], None] | None = None
        self._on_start_cb: Callable[[], None] | None = None

        self._started: bool = False
        self._alive: bool = True
        self._paused: bool = False

    # --- Chaining API ---

    def set_ease(self, ease: str | Callable[[float], float]) -> Tween:
        if isinstance(ease, str):
            self._ease_fn = EASINGS.get(ease, linear)
        else:
            self._ease_fn = ease
        return self

    def set_delay(self, delay: float) -> Tween:
        self._delay = delay
        return self

    def set_loops(self, count: int = -1, loop_type: LoopType = LoopType.RESTART) -> Tween:
        """Set looping. count: -1 = infinite, 0 = no loop, N = N extra loops."""
        self._loop_count = count
        self._loop_type = loop_type
        return self

    def on_complete(self, callback: Callable[[], None]) -> Tween:
        self._on_complete = callback
        return self

    def on_update(self, callback: Callable[[float], None]) -> Tween:
        """Called each frame with the current progress (0~1)."""
        self._on_update_cb = callback
        return self

    def on_start(self, callback: Callable[[], None]) -> Tween:
        self._on_start_cb = callback
        return self

    # --- Control ---

    def play(self) -> Tween:
        """Add this tween to the global tween manager."""
        _get_manager().add(self)
        return self

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def kill(self) -> None:
        self._alive = False

    def complete(self) -> None:
        """Jump to end immediately."""
        self._elapsed = self._duration
        self._apply(1.0)
        self._alive = False
        if self._on_complete:
            self._on_complete()

    @property
    def is_alive(self) -> bool:
        return self._alive

    @property
    def is_paused(self) -> bool:
        return self._paused

    # --- Internal ---

    def _update(self, dt: float) -> bool:
        """Returns False when tween should be removed."""
        if not self._alive or self._paused:
            return self._alive

        # Delay phase
        if self._delay_elapsed < self._delay:
            self._delay_elapsed += dt
            return True

        # First frame
        if not self._started:
            self._started = True
            if self._on_start_cb:
                self._on_start_cb()

        # Progress
        self._elapsed += dt

        if self._elapsed >= self._duration:
            # Finished one cycle
            if self._loop_type == LoopType.NONE:
                self._apply(1.0)
                self._alive = False
                if self._on_complete:
                    self._on_complete()
                return False

            # Looping
            self._loops_done += 1
            if self._loop_count != -1 and self._loops_done >= self._loop_count:
                self._apply(1.0 if self._forward else 0.0)
                self._alive = False
                if self._on_complete:
                    self._on_complete()
                return False

            self._elapsed -= self._duration

            if self._loop_type == LoopType.YOYO:
                self._forward = not self._forward
            # RESTART: stays forward
        else:
            t = self._elapsed / self._duration
            if not self._forward:
                t = 1.0 - t
            self._apply(t)

        return True

    def _apply(self, t: float) -> None:
        eased = self._ease_fn(t)
        value = _interpolate(self._start, self._end, eased)
        self._setter(value)
        if self._on_update_cb:
            self._on_update_cb(t)

    # --- Factory methods ---

    @staticmethod
    def to(
        getter: Callable[[], Any],
        setter: Callable[[Any], None],
        end_val: Any,
        duration: float,
    ) -> Tween:
        """Tween from current value to end_val."""
        start = getter()
        return Tween(getter, setter, start, end_val, duration)

    @staticmethod
    def from_to(
        setter: Callable[[Any], None],
        start_val: Any,
        end_val: Any,
        duration: float,
    ) -> Tween:
        """Tween from explicit start to end."""
        return Tween(lambda: start_val, setter, start_val, end_val, duration)

    @staticmethod
    def move(entity, target: Vector2, duration: float) -> Tween:
        """Tween entity position to target."""
        start = entity.position.copy()
        return Tween(
            lambda: entity.position,
            lambda v: setattr(entity, 'position', v),
            start, target, duration,
        )

    @staticmethod
    def scale_to(entity, target: Vector2, duration: float) -> Tween:
        """Tween entity scale to target."""
        start = entity.scale.copy()
        return Tween(
            lambda: entity.scale,
            lambda v: setattr(entity, 'scale', v),
            start, target, duration,
        )

    @staticmethod
    def rotate_to(entity, target: float, duration: float) -> Tween:
        """Tween entity rotation to target degrees."""
        start = entity.rotation
        return Tween(
            lambda: entity.rotation,
            lambda v: setattr(entity, 'rotation', v),
            start, target, duration,
        )

    @staticmethod
    def fade(component, target_alpha: float, duration: float) -> Tween:
        """Tween a component's 'opacity' or 'alpha' field."""
        start = getattr(component, 'opacity', getattr(component, 'alpha', 1.0))
        attr = 'opacity' if hasattr(component, 'opacity') else 'alpha'
        return Tween(
            lambda: getattr(component, attr),
            lambda v: setattr(component, attr, v),
            start, target_alpha, duration,
        )


def _interpolate(start: Any, end: Any, t: float) -> Any:
    """Interpolate between two values based on their type."""
    if isinstance(start, Vector2):
        return start.lerp(end, t)
    if isinstance(start, Color):
        return start.lerp(end, t)
    if isinstance(start, (int, float)):
        return start + (end - start) * t
    return end if t >= 1.0 else start


class TweenSequence:
    """Play tweens one after another.

    Example:
        seq = TweenSequence()
        seq.append(Tween.move(entity, Vector2(100, 100), 0.5))
        seq.append(Tween.move(entity, Vector2(400, 100), 0.5))
        seq.append_interval(0.3)  # wait 0.3s
        seq.append(Tween.move(entity, Vector2(400, 400), 0.5))
        seq.on_complete(lambda: print("Done!"))
        seq.play()
    """

    def __init__(self) -> None:
        self._tweens: list[Tween | float] = []  # Tween or interval (seconds)
        self._index: int = 0
        self._interval_timer: float = 0.0
        self._alive: bool = True
        self._on_complete: Callable[[], None] | None = None

    def append(self, tween: Tween) -> TweenSequence:
        self._tweens.append(tween)
        return self

    def append_interval(self, seconds: float) -> TweenSequence:
        self._tweens.append(seconds)
        return self

    def on_complete(self, callback: Callable[[], None]) -> TweenSequence:
        self._on_complete = callback
        return self

    def play(self) -> TweenSequence:
        _get_manager().add_sequence(self)
        return self

    def kill(self) -> None:
        self._alive = False

    @property
    def is_alive(self) -> bool:
        return self._alive

    def _update(self, dt: float) -> bool:
        if not self._alive:
            return False

        if self._index >= len(self._tweens):
            self._alive = False
            if self._on_complete:
                self._on_complete()
            return False

        current = self._tweens[self._index]

        if isinstance(current, (int, float)):
            # Interval
            self._interval_timer += dt
            if self._interval_timer >= current:
                self._interval_timer = 0.0
                self._index += 1
        elif isinstance(current, Tween):
            if not current._started and not current._alive:
                # Not yet started — activate it (don't add to manager)
                current._alive = True
            result = current._update(dt)
            if not result:
                self._index += 1

        return True


class TweenParallel:
    """Play tweens simultaneously.

    Example:
        par = TweenParallel()
        par.add(Tween.move(entity, Vector2(400, 300), 1.0))
        par.add(Tween.rotate_to(entity, 360, 1.0))
        par.on_complete(lambda: print("All done!"))
        par.play()
    """

    def __init__(self) -> None:
        self._tweens: list[Tween] = []
        self._alive: bool = True
        self._on_complete: Callable[[], None] | None = None

    def add(self, tween: Tween) -> TweenParallel:
        self._tweens.append(tween)
        return self

    def on_complete(self, callback: Callable[[], None]) -> TweenParallel:
        self._on_complete = callback
        return self

    def play(self) -> TweenParallel:
        _get_manager().add_parallel(self)
        return self

    def kill(self) -> None:
        self._alive = False

    @property
    def is_alive(self) -> bool:
        return self._alive

    def _update(self, dt: float) -> bool:
        if not self._alive:
            return False

        all_done = True
        for tw in self._tweens:
            if tw.is_alive:
                tw._update(dt)
            if tw.is_alive:
                all_done = False

        if all_done:
            self._alive = False
            if self._on_complete:
                self._on_complete()
            return False
        return True


class TweenManager(Component):
    """Component that drives all tweens. Add to a manager entity.

    Or use the global tween manager via Tween(...).play().

    Example:
        mgr = Entity("TweenManager")
        mgr.add_component(TweenManager())
        scene.add(mgr)
    """

    def __init__(self) -> None:
        super().__init__()
        self._tweens: list[Tween] = []
        self._sequences: list[TweenSequence] = []
        self._parallels: list[TweenParallel] = []

    def add(self, tween: Tween) -> None:
        self._tweens.append(tween)

    def add_sequence(self, seq: TweenSequence) -> None:
        self._sequences.append(seq)

    def add_parallel(self, par: TweenParallel) -> None:
        self._parallels.append(par)

    def kill_all(self) -> None:
        for tw in self._tweens:
            tw.kill()
        for seq in self._sequences:
            seq.kill()
        for par in self._parallels:
            par.kill()
        self._tweens.clear()
        self._sequences.clear()
        self._parallels.clear()

    def on_update(self, dt: float) -> None:
        self._tweens = [tw for tw in self._tweens if tw._update(dt)]
        self._sequences = [s for s in self._sequences if s._update(dt)]
        self._parallels = [p for p in self._parallels if p._update(dt)]

    def on_awake(self) -> None:
        global _global_manager
        if _global_manager is None:
            _global_manager = self


# Global tween manager
_global_manager: TweenManager | None = None


def _get_manager() -> TweenManager:
    if _global_manager is None:
        raise RuntimeError(
            "No TweenManager exists. Add a TweenManager component to an entity in your scene."
        )
    return _global_manager
