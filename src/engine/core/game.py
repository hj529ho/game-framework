from __future__ import annotations

from typing import TYPE_CHECKING

from engine.core.app import App
from engine.renderer.color import Color
from engine.scene.scene_manager import SceneManager

if TYPE_CHECKING:
    from engine.scene.scene import Scene


class Game:
    """Main engine entry point. Owns the SDL2 app and runs the game loop.

    The engine manages the lifecycle internally:
        init → [on_enter] → loop { poll → start → fixed_update(0~N) → update → late_update → draw } → [on_exit] → shutdown

    Game developers interact through Component lifecycle hooks and Scene hooks.

    Example:
        game = Game(title="My Game", width=800, height=600)
        game.run(MyScene())
    """

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
        self._app = App(
            title=title,
            width=width,
            height=height,
            fps=fps,
            vsync=vsync,
            resizable=resizable,
            clear_color=clear_color,
        )
        self._scenes = SceneManager()

    @property
    def app(self) -> App:
        return self._app

    @property
    def scenes(self) -> SceneManager:
        return self._scenes

    @property
    def width(self) -> int:
        return self._app.width

    @property
    def height(self) -> int:
        return self._app.height

    def quit(self) -> None:
        self._app.quit()

    def run(self, initial_scene: Scene) -> None:
        """Start the game loop with the given scene.

        Lifecycle per frame:
            1. Poll SDL events (input state updated)
            2. Clock tick (delta time calculated)
            3. Scene.update(dt)
               - World processes pending entity additions
               - Component.on_start() for new components
               - Component.on_fixed_update(fixed_dt) 0~N times (accumulator-based)
               - Component.on_update(dt) for all active components
               - Component.on_late_update(dt) for all active components
               - World processes pending entity removals
            4. Renderer.begin_frame() (clear screen)
            5. Scene.draw(renderer)
               - Component.on_draw(renderer) for all active components
            6. Renderer.end_frame() (present frame)
            7. SceneManager processes pending scene transitions
        """
        app = self._app
        scenes = self._scenes

        # Push initial scene
        scenes.push(initial_scene)
        scenes.process_pending()

        try:
            while app.running:
                # 1. Events
                app.poll_events()

                # 2. Timing
                dt = app.clock.tick()

                # 3. Update
                scenes.update(dt)

                # 4-6. Render
                app.renderer.begin_frame()
                scenes.draw(app.renderer)
                app.renderer.end_frame()
        finally:
            # Cleanup: exit all scenes
            scenes.clear()
            scenes.process_pending()
            app.destroy()
