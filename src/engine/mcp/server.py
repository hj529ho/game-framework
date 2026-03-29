"""MCP server for AI-driven game engine control.

Runs a FastMCP server in a background thread, exposing tools
for AI agents to inspect and manipulate the running game.
"""
from __future__ import annotations

import asyncio
import json
import threading
from typing import Any, TYPE_CHECKING

from mcp.server import FastMCP

if TYPE_CHECKING:
    from engine.core.game import Game


def _get_game() -> Game:
    from engine.core.app import current_app
    app = current_app()
    # Walk back to find the Game instance
    # Game stores itself on app._game_ref during run()
    game = getattr(app, '_game_ref', None)
    if game is None:
        raise RuntimeError("No Game instance found.")
    return game


def _get_scene():
    game = _get_game()
    scene = game.scenes.current
    if scene is None:
        raise RuntimeError("No active scene.")
    return scene


def _get_world():
    return _get_scene().world


def create_mcp_server(name: str = "game-engine") -> FastMCP:
    """Create and configure the MCP server with all game engine tools."""
    mcp = FastMCP(name)

    # ========================================================================
    # Entity tools
    # ========================================================================

    @mcp.tool()
    def list_entities() -> str:
        """List all entities in the current scene.
        Returns JSON array of {id, name, position, active, tags, components}."""
        world = _get_world()
        entities = []
        for e in world.entities:
            entities.append({
                "id": e.id,
                "name": e.name,
                "position": {"x": e.position.x, "y": e.position.y},
                "rotation": e.rotation,
                "scale": {"x": e.scale.x, "y": e.scale.y},
                "active": e.active,
                "tags": list(e.tags),
                "components": [type(c).__name__ for c in e.components],
            })
        return json.dumps(entities, indent=2)

    @mcp.tool()
    def get_entity(name: str) -> str:
        """Get detailed info about an entity by name.
        Returns JSON with id, name, position, rotation, scale, tags, components with their fields."""
        world = _get_world()
        entity = world.find_by_name(name)
        if entity is None:
            return json.dumps({"error": f"Entity '{name}' not found"})

        components = []
        for c in entity.components:
            comp_info = {
                "type": type(c).__name__,
                "enabled": c.enabled,
                "fields": {},
            }
            for attr in dir(c):
                if attr.startswith('_'):
                    continue
                try:
                    val = getattr(c, attr)
                    if callable(val):
                        continue
                    if isinstance(val, (int, float, str, bool)):
                        comp_info["fields"][attr] = val
                except Exception:
                    pass
            components.append(comp_info)

        result = {
            "id": entity.id,
            "name": entity.name,
            "position": {"x": entity.position.x, "y": entity.position.y},
            "rotation": entity.rotation,
            "scale": {"x": entity.scale.x, "y": entity.scale.y},
            "active": entity.active,
            "tags": list(entity.tags),
            "components": components,
        }
        return json.dumps(result, indent=2)

    @mcp.tool()
    def create_entity(name: str, x: float = 0, y: float = 0) -> str:
        """Create a new entity and add it to the current scene.
        Returns the entity's id and name."""
        from engine.ecs.entity import Entity
        from engine.math.vector2 import Vector2

        entity = Entity(name)
        entity.position = Vector2(x, y)
        _get_scene().add(entity)
        return json.dumps({"id": entity.id, "name": entity.name})

    @mcp.tool()
    def destroy_entity(name: str) -> str:
        """Remove an entity from the current scene by name."""
        world = _get_world()
        entity = world.find_by_name(name)
        if entity is None:
            return json.dumps({"error": f"Entity '{name}' not found"})
        world.remove(entity)
        return json.dumps({"status": "destroyed", "name": name})

    # ========================================================================
    # Transform tools
    # ========================================================================

    @mcp.tool()
    def set_position(name: str, x: float, y: float) -> str:
        """Set an entity's position."""
        from engine.math.vector2 import Vector2
        entity = _get_world().find_by_name(name)
        if entity is None:
            return json.dumps({"error": f"Entity '{name}' not found"})
        entity.position = Vector2(x, y)
        return json.dumps({"name": name, "position": {"x": x, "y": y}})

    @mcp.tool()
    def set_rotation(name: str, degrees: float) -> str:
        """Set an entity's rotation in degrees."""
        entity = _get_world().find_by_name(name)
        if entity is None:
            return json.dumps({"error": f"Entity '{name}' not found"})
        entity.rotation = degrees
        return json.dumps({"name": name, "rotation": degrees})

    @mcp.tool()
    def set_scale(name: str, x: float, y: float) -> str:
        """Set an entity's scale."""
        from engine.math.vector2 import Vector2
        entity = _get_world().find_by_name(name)
        if entity is None:
            return json.dumps({"error": f"Entity '{name}' not found"})
        entity.scale = Vector2(x, y)
        return json.dumps({"name": name, "scale": {"x": x, "y": y}})

    # ========================================================================
    # Component tools
    # ========================================================================

    @mcp.tool()
    def add_component(entity_name: str, component_type: str, **kwargs) -> str:
        """Add a built-in component to an entity by type name.
        Supported types: BoxCollider, CircleCollider, SpriteRenderer, TextRenderer, Camera2D.
        Additional kwargs are set as attributes on the component."""
        entity = _get_world().find_by_name(entity_name)
        if entity is None:
            return json.dumps({"error": f"Entity '{entity_name}' not found"})

        comp = _create_component(component_type, kwargs)
        if comp is None:
            return json.dumps({"error": f"Unknown component type '{component_type}'"})

        entity.add_component(comp)
        return json.dumps({
            "entity": entity_name,
            "component": component_type,
            "status": "added",
        })

    @mcp.tool()
    def remove_component(entity_name: str, component_type: str) -> str:
        """Remove a component by type name from an entity."""
        entity = _get_world().find_by_name(entity_name)
        if entity is None:
            return json.dumps({"error": f"Entity '{entity_name}' not found"})

        comp_class = _resolve_component_class(component_type)
        if comp_class is None:
            return json.dumps({"error": f"Unknown component type '{component_type}'"})

        comp = entity.get_component(comp_class)
        if comp is None:
            return json.dumps({"error": f"Entity '{entity_name}' has no {component_type}"})

        entity.remove_component(comp)
        return json.dumps({"entity": entity_name, "component": component_type, "status": "removed"})

    @mcp.tool()
    def get_component_state(entity_name: str, component_type: str) -> str:
        """Get all readable fields of a component."""
        entity = _get_world().find_by_name(entity_name)
        if entity is None:
            return json.dumps({"error": f"Entity '{entity_name}' not found"})

        comp_class = _resolve_component_class(component_type)
        if comp_class is None:
            return json.dumps({"error": f"Unknown component type '{component_type}'"})

        comp = entity.get_component(comp_class)
        if comp is None:
            return json.dumps({"error": f"No {component_type} on '{entity_name}'"})

        fields = {}
        for attr in dir(comp):
            if attr.startswith('_'):
                continue
            try:
                val = getattr(comp, attr)
                if callable(val):
                    continue
                if isinstance(val, (int, float, str, bool)):
                    fields[attr] = val
            except Exception:
                pass

        return json.dumps({"entity": entity_name, "component": component_type, "fields": fields}, indent=2)

    @mcp.tool()
    def set_component_field(entity_name: str, component_type: str, field: str, value: Any) -> str:
        """Set a field on a component."""
        entity = _get_world().find_by_name(entity_name)
        if entity is None:
            return json.dumps({"error": f"Entity '{entity_name}' not found"})

        comp_class = _resolve_component_class(component_type)
        if comp_class is None:
            return json.dumps({"error": f"Unknown component type '{component_type}'"})

        comp = entity.get_component(comp_class)
        if comp is None:
            return json.dumps({"error": f"No {component_type} on '{entity_name}'"})

        if not hasattr(comp, field):
            return json.dumps({"error": f"Field '{field}' not found on {component_type}"})

        setattr(comp, field, value)
        return json.dumps({"entity": entity_name, "component": component_type, "field": field, "value": value})

    # ========================================================================
    # Scene tools
    # ========================================================================

    @mcp.tool()
    def list_scenes() -> str:
        """List the scene stack."""
        game = _get_game()
        sm = game.scenes
        scenes = []
        for i, s in enumerate(sm._stack):
            scenes.append({
                "index": i,
                "name": s.name,
                "entity_count": len(s.world),
                "is_current": (i == len(sm._stack) - 1),
            })
        return json.dumps(scenes, indent=2)

    @mcp.tool()
    def pop_scene() -> str:
        """Pop the current scene from the stack."""
        game = _get_game()
        if game.scenes.stack_depth <= 1:
            return json.dumps({"error": "Cannot pop the last scene"})
        game.scenes.pop()
        return json.dumps({"status": "popped"})

    # ========================================================================
    # Engine state tools
    # ========================================================================

    @mcp.tool()
    def get_engine_state() -> str:
        """Get engine state: FPS, frame count, total time, window size."""
        from engine.core.app import current_app
        app = current_app()
        return json.dumps({
            "fps": round(app.clock.fps, 1),
            "frame_count": app.clock.frame_count,
            "total_time": round(app.clock.total_time, 2),
            "dt": round(app.clock.dt, 4),
            "window": {"width": app.width, "height": app.height},
        }, indent=2)

    @mcp.tool()
    def get_input_state() -> str:
        """Get current keyboard and mouse state."""
        from engine.core.app import current_app
        app = current_app()
        mouse = app.mouse
        return json.dumps({
            "mouse": {
                "position": {"x": mouse.position.x, "y": mouse.position.y},
                "scroll_delta": mouse.scroll_delta,
            },
        })

    @mcp.tool()
    def execute_code(code: str) -> str:
        """Execute Python code in the engine context. Use for advanced operations.
        Has access to: engine module, current scene, current app.
        Returns the string representation of the last expression, or error."""
        import engine
        from engine.core.app import current_app

        local_vars = {
            "engine": engine,
            "app": current_app(),
            "scene": _get_scene(),
            "world": _get_world(),
        }

        try:
            # Try eval first (expression)
            result = eval(code, {"__builtins__": __builtins__}, local_vars)
            return json.dumps({"result": str(result)})
        except SyntaxError:
            # Fall back to exec (statement)
            try:
                exec(code, {"__builtins__": __builtins__}, local_vars)
                return json.dumps({"status": "executed"})
            except Exception as e:
                return json.dumps({"error": str(e)})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def quit_game() -> str:
        """Quit the game."""
        from engine.core.app import current_app
        current_app().quit()
        return json.dumps({"status": "quitting"})

    return mcp


# ============================================================================
# Component resolution helpers
# ============================================================================

_COMPONENT_MAP: dict[str, type] | None = None


def _get_component_map() -> dict[str, type]:
    global _COMPONENT_MAP
    if _COMPONENT_MAP is None:
        from engine.physics.collider import BoxCollider, CircleCollider
        from engine.renderer.sprite import SpriteRenderer
        from engine.renderer.text import TextRenderer
        from engine.renderer.camera import Camera2D
        from engine.physics.physics_world import PhysicsWorld
        from engine.tween.tween import TweenManager

        _COMPONENT_MAP = {
            "BoxCollider": BoxCollider,
            "CircleCollider": CircleCollider,
            "SpriteRenderer": SpriteRenderer,
            "TextRenderer": TextRenderer,
            "Camera2D": Camera2D,
            "PhysicsWorld": PhysicsWorld,
            "TweenManager": TweenManager,
        }
    return _COMPONENT_MAP


def _resolve_component_class(name: str) -> type | None:
    return _get_component_map().get(name)


def _create_component(type_name: str, kwargs: dict) -> Any:
    cls = _resolve_component_class(type_name)
    if cls is None:
        return None

    from engine.physics.collider import BoxCollider, CircleCollider
    from engine.renderer.sprite import SpriteRenderer
    from engine.renderer.text import TextRenderer
    from engine.renderer.camera import Camera2D

    if cls is BoxCollider:
        return BoxCollider(kwargs.get("width", 32), kwargs.get("height", 32))
    elif cls is CircleCollider:
        return CircleCollider(kwargs.get("radius", 16))
    elif cls is SpriteRenderer:
        return SpriteRenderer(kwargs.get("image", ""))
    elif cls is TextRenderer:
        return TextRenderer(
            text=kwargs.get("text", ""),
            font=kwargs.get("font", ""),
            font_size=kwargs.get("font_size", 16),
        )
    elif cls is Camera2D:
        return Camera2D(kwargs.get("width", 800), kwargs.get("height", 600))
    else:
        return cls()


# ============================================================================
# Server runner
# ============================================================================

def run_mcp_server_thread(server: FastMCP, transport: str = "stdio") -> threading.Thread:
    """Run the MCP server in a background thread.

    Args:
        server: The FastMCP server instance.
        transport: "stdio" (default) or "sse".

    Returns:
        The started thread.
    """
    def _run():
        server.run(transport=transport)

    thread = threading.Thread(target=_run, daemon=True, name="mcp-server")
    thread.start()
    return thread
