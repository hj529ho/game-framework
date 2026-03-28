from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any
from collections import defaultdict


@dataclass(frozen=True)
class Event:
    """Base event class. Subclass with dataclass for custom events.

    Example:
        @dataclass(frozen=True)
        class PlayerDiedEvent(Event):
            player_name: str
            killer_name: str
    """
    pass


# Built-in engine events

@dataclass(frozen=True)
class SceneChangedEvent(Event):
    old_scene: str
    new_scene: str


@dataclass(frozen=True)
class EntityCreatedEvent(Event):
    entity_name: str


@dataclass(frozen=True)
class EntityDestroyedEvent(Event):
    entity_name: str


@dataclass(frozen=True)
class CollisionEvent(Event):
    entity_a: str
    entity_b: str


class EventBus:
    """Decoupled publish/subscribe event system.

    Components emit events; any other component can listen without
    needing a direct reference.

    Example:
        bus = EventBus()

        # Subscribe
        bus.on(PlayerDiedEvent, self.handle_death)

        # Emit
        bus.emit(PlayerDiedEvent(player_name="Hero", killer_name="Boss"))

        # Unsubscribe
        bus.off(PlayerDiedEvent, self.handle_death)
    """

    def __init__(self) -> None:
        self._listeners: dict[type, list[tuple[int, Callable]]] = defaultdict(list)

    def on(self, event_type: type[Event], callback: Callable[[Event], None],
           priority: int = 0) -> None:
        """Subscribe to an event type. Lower priority runs first."""
        listeners = self._listeners[event_type]
        listeners.append((priority, callback))
        listeners.sort(key=lambda x: x[0])

    def off(self, event_type: type[Event], callback: Callable) -> None:
        """Unsubscribe from an event type."""
        listeners = self._listeners[event_type]
        self._listeners[event_type] = [
            (p, cb) for p, cb in listeners if cb is not callback
        ]

    def emit(self, event: Event) -> None:
        """Emit an event to all subscribers of its type."""
        for _, callback in self._listeners.get(type(event), []):
            callback(event)

    def clear(self, event_type: type[Event] | None = None) -> None:
        """Clear listeners. If event_type is None, clear all."""
        if event_type is None:
            self._listeners.clear()
        else:
            self._listeners.pop(event_type, None)


# Global event bus (accessible from anywhere)
_global_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus. Created on first access."""
    global _global_bus
    if _global_bus is None:
        _global_bus = EventBus()
    return _global_bus
