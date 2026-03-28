# engine.core.events -- API Reference

## Class: `Event`

**File**: `events.py`

Base event. Subclass with `@dataclass(frozen=True)` for custom events.

```python
@dataclass(frozen=True)
class PlayerDiedEvent(Event):
    player_name: str
    killer_name: str
```

---

## Class: `EventBus`

**File**: `events.py`

Decoupled publish/subscribe. Components emit events without needing direct references.

### Methods

| Method | Signature | Description |
|---|---|---|
| `on` | `(event_type, callback, priority=0)` | Subscribe. Lower priority runs first. |
| `off` | `(event_type, callback)` | Unsubscribe. |
| `emit` | `(event: Event)` | Emit to all subscribers of that type. |
| `clear` | `(event_type=None)` | Clear listeners. None = clear all. |

### Usage

```python
class DamageSystem(Component):
    def on_start(self):
        get_event_bus().on(DamageEvent, self.handle)

    def handle(self, event):
        print(f"{event.target} took {event.amount} damage")

    def on_destroy(self):
        get_event_bus().off(DamageEvent, self.handle)
```

---

## Function: `get_event_bus`

```python
get_event_bus() -> EventBus
```

Returns the global event bus singleton. Created on first access.
