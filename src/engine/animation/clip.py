from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class FrameEvent:
    """Callback triggered at a specific frame."""
    frame: int
    callback: Callable[[], None]


@dataclass
class AnimationClip:
    """A single animation: frame list, speed, loop, and per-frame events.

    Example:
        clip = AnimationClip(
            name="attack",
            frames=[0, 1, 2, 3, 4],
            fps=12,
            loop=False,
        )
        clip.add_event(2, lambda: print("Slash!"))
        clip.add_event(4, lambda: print("Done!"))
    """
    name: str
    frames: list[int]
    fps: float = 10.0
    loop: bool = True
    events: list[FrameEvent] = field(default_factory=list)

    def add_event(self, frame: int, callback: Callable[[], None]) -> None:
        """Register a callback to fire when this frame is reached."""
        self.events.append(FrameEvent(frame, callback))

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def duration(self) -> float:
        """Total duration in seconds."""
        if self.fps <= 0:
            return 0.0
        return len(self.frames) / self.fps
