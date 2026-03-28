from __future__ import annotations

import ctypes

from sdl2 import (
    SDL_Init, SDL_Quit, SDL_INIT_VIDEO, SDL_INIT_AUDIO,
    SDL_CreateWindow, SDL_DestroyWindow,
    SDL_CreateRenderer, SDL_DestroyRenderer,
    SDL_WINDOWPOS_CENTERED,
    SDL_WINDOW_SHOWN, SDL_WINDOW_RESIZABLE,
    SDL_RENDERER_ACCELERATED, SDL_RENDERER_PRESENTVSYNC,
    SDL_PollEvent, SDL_Event, SDL_QUIT,
)

from engine.core.clock import Clock
from engine.input.keyboard import Keyboard
from engine.input.mouse import Mouse
from engine.renderer.renderer import Renderer
from engine.renderer.color import Color
from engine.resources.resource_manager import ResourceManager


# Module-level reference to current app instance
_current_app: App | None = None


def current_app() -> App:
    if _current_app is None:
        raise RuntimeError("No App instance is running.")
    return _current_app


class App:
    """Low-level application wrapper. User controls the game loop."""

    def __init__(
        self,
        title: str = "Game",
        width: int = 800,
        height: int = 600,
        fps: int = 60,
        vsync: bool = True,
        resizable: bool = False,
        clear_color: Color | None = None,
    ) -> None:
        global _current_app

        self._width = width
        self._height = height
        self._running = False

        # Init SDL2
        if SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO) != 0:
            from sdl2 import SDL_GetError
            raise RuntimeError(f"SDL2 init failed: {SDL_GetError()}")

        # Create window
        flags = SDL_WINDOW_SHOWN
        if resizable:
            flags |= SDL_WINDOW_RESIZABLE

        self._window = SDL_CreateWindow(
            title.encode('utf-8'),
            SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
            width, height,
            flags,
        )
        if not self._window:
            from sdl2 import SDL_GetError
            SDL_Quit()
            raise RuntimeError(f"Window creation failed: {SDL_GetError()}")

        # Create renderer
        renderer_flags = SDL_RENDERER_ACCELERATED
        if vsync:
            renderer_flags |= SDL_RENDERER_PRESENTVSYNC

        sdl_renderer = SDL_CreateRenderer(self._window, -1, renderer_flags)
        if not sdl_renderer:
            from sdl2 import SDL_GetError
            SDL_DestroyWindow(self._window)
            SDL_Quit()
            raise RuntimeError(f"Renderer creation failed: {SDL_GetError()}")

        # Create subsystems
        self._clock = Clock(fps)
        self._keyboard = Keyboard()
        self._mouse = Mouse()
        self._renderer = Renderer(sdl_renderer)
        self._renderer.clear_color = clear_color or Color(30, 30, 30)
        self._resources = ResourceManager(sdl_renderer)
        self._sdl_renderer = sdl_renderer
        self._running = True
        _current_app = self

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def running(self) -> bool:
        return self._running

    @property
    def clock(self) -> Clock:
        return self._clock

    @property
    def keyboard(self) -> Keyboard:
        return self._keyboard

    @property
    def mouse(self) -> Mouse:
        return self._mouse

    @property
    def renderer(self) -> Renderer:
        return self._renderer

    @property
    def resources(self) -> ResourceManager:
        return self._resources

    def poll_events(self) -> None:
        """Poll SDL events. Call once per frame before update logic."""
        self._keyboard.update()
        self._mouse.update()

        event = SDL_Event()
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                self._running = False
            self._keyboard.process_event(event)
            self._mouse.process_event(event)

    def quit(self) -> None:
        self._running = False

    def destroy(self) -> None:
        global _current_app
        self._resources.destroy()
        if self._sdl_renderer:
            SDL_DestroyRenderer(self._sdl_renderer)
            self._sdl_renderer = None
        if self._window:
            SDL_DestroyWindow(self._window)
            self._window = None
        SDL_Quit()
        _current_app = None
