from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.renderer.renderer import Renderer


class Lifecycle:
    """Base class defining game object lifecycle hooks.

    Inherit from this (via Component) and override the methods you need.
    The engine calls these automatically in the following order each frame:

        First frame only:
            on_awake()   -> called when component is added to an entity
            on_start()   -> called once before the first on_update

        Every frame (may run 0~N times per frame at fixed interval):
            on_fixed_update(fixed_dt) -> physics, deterministic logic

        Every frame (once):
            on_update(dt)       -> game logic, input handling
            on_late_update(dt)  -> post-update (camera follow, constraints)

        Render phase:
            on_draw(renderer)   -> visual representation

        Cleanup:
            on_destroy()        -> called when component is removed or entity is destroyed
    """

    def on_awake(self) -> None:
        """Called immediately when this component is added to an entity.
        Use for field initialization that depends on the entity reference.
        """
        pass

    def on_start(self) -> None:
        """Called once before the first on_update.
        All components on the entity are guaranteed to be awake.
        Use for initialization that depends on other components.
        """
        pass

    def on_fixed_update(self, fixed_dt: float) -> None:
        """Called at a fixed time interval (default 1/50s = 20ms).
        May run 0, 1, or multiple times per frame depending on frame rate.
        Use for physics, collision response, and any deterministic simulation.
        The fixed_dt is always the same value (fixed_timestep).
        """
        pass

    def on_update(self, dt: float) -> None:
        """Called once every frame. Use for game logic, input, movement."""
        pass

    def on_late_update(self, dt: float) -> None:
        """Called every frame after all on_update calls are done.
        Use for camera follow, UI sync, constraints that depend on updated positions.
        """
        pass

    def on_draw(self, renderer: Renderer) -> None:
        """Called every frame during render phase.
        Use for drawing sprites, shapes, debug visuals.
        """
        pass

    def on_destroy(self) -> None:
        """Called when this component is removed from the entity,
        or when the entity is removed from the world.
        Use for cleanup (release resources, unsubscribe events).
        """
        pass
