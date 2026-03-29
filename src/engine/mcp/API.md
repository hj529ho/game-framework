# engine.mcp -- API Reference

MCP (Model Context Protocol) server for AI-driven game engine control.
Allows AI agents to inspect and manipulate a running game in real-time.

## Enabling MCP

```python
game = Game(title="AI Game", width=800, height=600, mcp=True)
game.run(MyScene())  # MCP server starts in background thread
```

| Game Parameter | Type | Default | Description |
|---|---|---|---|
| `mcp` | `bool` | `False` | Enable MCP server |
| `mcp_transport` | `str` | `"stdio"` | Transport: `"stdio"` or `"sse"` |

---

## MCP Tools

All tools return JSON strings.

### Entity Tools

#### `list_entities`
List all entities in the current scene.
- **Parameters**: none
- **Returns**: JSON array of `{id, name, position: {x, y}, rotation, scale: {x, y}, active, tags, components}`

#### `get_entity`
Get detailed info about an entity by name.
- **Parameters**: `name: str`
- **Returns**: JSON with full entity data including component fields

#### `create_entity`
Create a new entity and add it to the current scene.
- **Parameters**: `name: str`, `x: float = 0`, `y: float = 0`
- **Returns**: `{id, name}`

#### `destroy_entity`
Remove an entity from the current scene.
- **Parameters**: `name: str`
- **Returns**: `{status: "destroyed", name}`

### Transform Tools

#### `set_position`
- **Parameters**: `name: str`, `x: float`, `y: float`

#### `set_rotation`
- **Parameters**: `name: str`, `degrees: float`

#### `set_scale`
- **Parameters**: `name: str`, `x: float`, `y: float`

### Component Tools

#### `add_component`
Add a built-in component to an entity.
- **Parameters**: `entity_name: str`, `component_type: str`, `**kwargs`
- **Supported types**: `BoxCollider`, `CircleCollider`, `SpriteRenderer`, `TextRenderer`, `Camera2D`, `PhysicsWorld`, `TweenManager`

#### `remove_component`
- **Parameters**: `entity_name: str`, `component_type: str`

#### `get_component_state`
Get all readable fields of a component.
- **Parameters**: `entity_name: str`, `component_type: str`
- **Returns**: JSON with field names and values

#### `set_component_field`
Set a field on a component.
- **Parameters**: `entity_name: str`, `component_type: str`, `field: str`, `value: Any`

### Scene Tools

#### `list_scenes`
List the scene stack.
- **Returns**: JSON array of `{index, name, entity_count, is_current}`

#### `pop_scene`
Pop the current scene. Fails if only one scene on stack.

### Engine State Tools

#### `get_engine_state`
- **Returns**: `{fps, frame_count, total_time, dt, window: {width, height}}`

#### `get_input_state`
- **Returns**: `{mouse: {position: {x, y}, scroll_delta}}`

#### `execute_code`
Execute Python code in the engine context.
- **Parameters**: `code: str`
- **Available variables**: `engine`, `app`, `scene`, `world`
- **Returns**: `{result: "..."}` for expressions, `{status: "executed"}` for statements, `{error: "..."}` on failure

#### `quit_game`
Quit the game.

---

## Functions

### `create_mcp_server`

```python
create_mcp_server(name: str = "game-engine") -> FastMCP
```

Create and configure the MCP server with all game engine tools.

### `run_mcp_server_thread`

```python
run_mcp_server_thread(server: FastMCP, transport: str = "stdio") -> threading.Thread
```

Run the MCP server in a daemon background thread. Returns the started thread.

---

## Architecture

```
Game.run(scene, mcp=True)
  |
  +-- MCP server (background thread)
  |     |-- stdio/sse transport
  |     |-- AI agent connects
  |     |-- Tool calls -> read/modify game state
  |
  +-- Game loop (main thread)
        |-- poll_events
        |-- update (entities, components)
        |-- draw
```

MCP tools access game state through `current_app()` and the Game reference stored on `app._game_ref`. All tool calls execute synchronously on the MCP thread but read/write shared game state. For thread safety, tools should only modify state that the game loop reads (positions, flags), not structural changes during iteration.
