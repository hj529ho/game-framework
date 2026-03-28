from __future__ import annotations

from sdl2 import SDL_GetPerformanceCounter, SDL_GetPerformanceFrequency, SDL_Delay


class Clock:
    def __init__(self, target_fps: int = 60) -> None:
        self._target_fps = target_fps
        self._freq = SDL_GetPerformanceFrequency()
        self._last = SDL_GetPerformanceCounter()
        self._dt: float = 0.0
        self._total_time: float = 0.0
        self._frame_count: int = 0
        self._fps: float = 0.0
        self._fps_accumulator: float = 0.0
        self._fps_frame_count: int = 0

    def tick(self) -> float:
        now = SDL_GetPerformanceCounter()
        self._dt = (now - self._last) / self._freq
        self._last = now

        # Cap minimum frame time to target FPS
        target_dt = 1.0 / self._target_fps
        if self._dt < target_dt:
            delay_ms = int((target_dt - self._dt) * 1000)
            if delay_ms > 0:
                SDL_Delay(delay_ms)
            now = SDL_GetPerformanceCounter()
            self._dt = (now - (self._last - int(self._dt * self._freq))) / self._freq
            self._last = now

        self._total_time += self._dt
        self._frame_count += 1

        # FPS calculation (updated every 0.5 seconds)
        self._fps_accumulator += self._dt
        self._fps_frame_count += 1
        if self._fps_accumulator >= 0.5:
            self._fps = self._fps_frame_count / self._fps_accumulator
            self._fps_accumulator = 0.0
            self._fps_frame_count = 0

        return self._dt

    @property
    def dt(self) -> float:
        return self._dt

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def total_time(self) -> float:
        return self._total_time

    @property
    def frame_count(self) -> int:
        return self._frame_count

    @property
    def target_fps(self) -> int:
        return self._target_fps

    @target_fps.setter
    def target_fps(self, value: int) -> None:
        self._target_fps = value
