"""Tests for engine.ecs module."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from engine.ecs.entity import Entity
from engine.ecs.component import Component
from engine.ecs.world import World
from engine.math.vector2 import Vector2


class Counter(Component):
    def on_awake(self):
        self.awake_count = 1
        self.start_count = 0
        self.update_count = 0
        self.fixed_count = 0
        self.late_count = 0
        self.destroyed = False

    def on_start(self):
        self.start_count += 1

    def on_update(self, dt):
        self.update_count += 1

    def on_fixed_update(self, fixed_dt):
        self.fixed_count += 1

    def on_late_update(self, dt):
        self.late_count += 1

    def on_destroy(self):
        self.destroyed = True


class Mover(Component):
    def on_start(self):
        self.speed = 100.0

    def on_update(self, dt):
        self.transform.translate(Vector2(self.speed * dt, 0))


# --- Entity ---

def test_entity_creation():
    e = Entity("Player")
    assert e.name == "Player"
    assert e.position == Vector2.zero()

def test_entity_auto_name():
    e = Entity()
    assert e.name.startswith("Entity_")

def test_entity_transform_shortcuts():
    e = Entity()
    e.position = Vector2(10, 20)
    e.rotation = 45.0
    e.scale = Vector2(2, 2)
    assert e.position == Vector2(10, 20)
    assert e.rotation == 45.0
    assert e.scale == Vector2(2, 2)

def test_entity_add_component():
    e = Entity("A")
    c = e.add_component(Counter())
    assert c.awake_count == 1  # on_awake called
    assert c.entity is e

def test_entity_get_component():
    e = Entity()
    e.add_component(Counter())
    assert e.get_component(Counter) is not None
    assert e.get_component(Mover) is None

def test_entity_has_component():
    e = Entity()
    e.add_component(Counter())
    assert e.has_component(Counter)
    assert not e.has_component(Mover)

def test_entity_remove_component():
    e = Entity()
    c = e.add_component(Counter())
    e.remove_component(c)
    assert c.destroyed
    assert not e.has_component(Counter)

def test_entity_get_components_multiple():
    e = Entity()
    c1 = e.add_component(Counter())
    c2 = e.add_component(Mover())
    assert len(e.components) == 2
    assert e.get_components(Component) == [c1, c2]

def test_entity_tags():
    e = Entity()
    e.add_tag("enemy")
    e.add_tag("boss")
    assert e.has_tag("enemy")
    assert e.has_tag("boss")
    assert not e.has_tag("player")

def test_entity_hierarchy():
    parent = Entity("Parent")
    child = Entity("Child")
    parent.add_child(child)
    assert child.parent is parent
    assert child in parent.children
    parent.remove_child(child)
    assert child.parent is None

def test_entity_game_ui():
    e = Entity()
    assert e._game_ui_root is None  # lazy
    ui = e.game_ui
    assert ui is not None
    assert e.game_ui is ui  # same instance

def test_entity_component_already_attached():
    e1 = Entity("A")
    e2 = Entity("B")
    c = Counter()
    e1.add_component(c)
    try:
        e2.add_component(c)
        assert False, "Should raise ValueError"
    except ValueError:
        pass


# --- World ---

def test_world_add_remove():
    w = World()
    e = Entity("A")
    w.add(e)
    w.update(0.016)
    assert len(w) == 1
    w.remove(e)
    w.update(0.016)
    assert len(w) == 0

def test_world_lifecycle_order():
    w = World()
    e = Entity()
    c = e.add_component(Counter())
    w.add(e)
    w.update(0.016)
    assert c.start_count == 1
    assert c.update_count == 1
    assert c.late_count == 1
    w.update(0.016)
    assert c.start_count == 1  # only once
    assert c.update_count == 2

def test_world_fixed_update():
    w = World(fixed_timestep=0.02)
    e = Entity()
    c = e.add_component(Counter())
    w.add(e)

    # 3 frames at ~30fps
    for _ in range(3):
        w.update(1.0 / 30.0)

    assert c.fixed_count > c.update_count
    assert c.update_count == 3

def test_world_deferred_add():
    w = World()
    e = Entity()
    c = e.add_component(Counter())
    w.add(e)
    # Not yet in entities
    assert len(w) == 0
    w.update(0.016)
    assert len(w) == 1

def test_world_clear():
    w = World()
    e = Entity()
    c = e.add_component(Counter())
    w.add(e)
    w.update(0.016)
    w.clear()
    assert len(w) == 0
    assert c.destroyed

def test_world_find_by_name():
    w = World()
    e = Entity("Target")
    w.add(e)
    w.update(0.016)
    assert w.find_by_name("Target") is e
    assert w.find_by_name("Missing") is None

def test_world_find_by_tag():
    w = World()
    e1 = Entity("A")
    e1.add_tag("enemy")
    e2 = Entity("B")
    e2.add_tag("enemy")
    e3 = Entity("C")
    w.add(e1)
    w.add(e2)
    w.add(e3)
    w.update(0.016)
    assert len(w.find_by_tag("enemy")) == 2

def test_world_find_with_component():
    w = World()
    e1 = Entity()
    e1.add_component(Counter())
    e2 = Entity()
    e2.add_component(Mover())
    e3 = Entity()
    e3.add_component(Counter())
    e3.add_component(Mover())
    w.add(e1)
    w.add(e2)
    w.add(e3)
    w.update(0.016)
    assert len(w.find_with_component(Counter)) == 2
    assert len(w.find_with_component(Counter, Mover)) == 1

def test_world_inactive_entity():
    w = World()
    e = Entity()
    c = e.add_component(Counter())
    e.active = False
    w.add(e)
    w.update(0.016)
    assert c.update_count == 0

def test_component_enabled():
    w = World()
    e = Entity()
    c = e.add_component(Counter())
    c.enabled = False
    w.add(e)
    w.update(0.016)
    assert c.start_count == 0
    assert c.update_count == 0
