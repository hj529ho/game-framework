"""Tests for engine.physics module."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from engine.math.vector2 import Vector2
from engine.ecs.entity import Entity
from engine.physics.collider import BoxCollider, CircleCollider
from engine.physics.collision import test_collision as check_collision, raycast, raycast_all, CollisionInfo, RaycastHit
from engine.physics.spatial_hash import SpatialHash


def _make_box(x, y, w, h):
    e = Entity()
    e.position = Vector2(x, y)
    return e.add_component(BoxCollider(w, h))


def _make_circle(x, y, r):
    e = Entity()
    e.position = Vector2(x, y)
    return e.add_component(CircleCollider(r))


# --- Collision detection ---

def test_aabb_aabb_hit():
    a = _make_box(100, 100, 40, 40)
    b = _make_box(130, 100, 40, 40)
    info = check_collision(a, b)
    assert info is not None
    assert info.penetration > 0

def test_aabb_aabb_miss():
    a = _make_box(0, 0, 10, 10)
    b = _make_box(100, 100, 10, 10)
    assert check_collision(a, b) is None

def test_circle_circle_hit():
    a = _make_circle(0, 0, 20)
    b = _make_circle(30, 0, 20)
    info = check_collision(a, b)
    assert info is not None
    assert abs(info.penetration - 10.0) < 0.01

def test_circle_circle_miss():
    a = _make_circle(0, 0, 10)
    b = _make_circle(100, 0, 10)
    assert check_collision(a, b) is None

def test_aabb_circle_hit():
    box = _make_box(100, 100, 40, 40)
    circle = _make_circle(130, 100, 20)
    info = check_collision(box, circle)
    assert info is not None

def test_circle_aabb_hit():
    box = _make_box(100, 100, 40, 40)
    circle = _make_circle(130, 100, 20)
    info = check_collision(circle, box)
    assert info is not None

def test_collision_normal():
    a = _make_box(100, 100, 40, 40)
    b = _make_box(130, 100, 40, 40)
    info = check_collision(a, b)
    assert info.normal.sqr_magnitude > 0


# --- Spatial hash ---

def test_spatial_hash_pairs():
    sh = SpatialHash(64)
    a = _make_box(10, 10, 20, 20)
    b = _make_box(20, 10, 20, 20)
    c = _make_box(500, 500, 20, 20)
    sh.insert(a)
    sh.insert(b)
    sh.insert(c)
    pairs = sh.get_candidate_pairs()
    assert len(pairs) >= 1
    # a and b should be candidates, c should not pair with them

def test_spatial_hash_query():
    sh = SpatialHash(64)
    a = _make_box(10, 10, 20, 20)
    b = _make_box(20, 10, 20, 20)
    sh.insert(a)
    sh.insert(b)
    result = sh.query(a)
    assert b in result

def test_spatial_hash_clear():
    sh = SpatialHash(64)
    sh.insert(_make_box(0, 0, 10, 10))
    sh.clear()
    assert sh.get_candidate_pairs() == []


# --- Raycast ---

def test_raycast_hit_box():
    box = _make_box(200, 100, 50, 50)
    hit = raycast(Vector2(0, 100), Vector2(1, 0), [box])
    assert hit is not None
    assert hit.collider is box
    assert hit.distance > 0

def test_raycast_hit_circle():
    circle = _make_circle(200, 100, 30)
    hit = raycast(Vector2(0, 100), Vector2(1, 0), [circle])
    assert hit is not None
    assert hit.collider is circle

def test_raycast_miss():
    box = _make_box(200, 100, 50, 50)
    hit = raycast(Vector2(0, 500), Vector2(1, 0), [box])
    assert hit is None

def test_raycast_max_distance():
    box = _make_box(200, 100, 50, 50)
    hit = raycast(Vector2(0, 100), Vector2(1, 0), [box], max_distance=100)
    assert hit is None

def test_raycast_layer_mask():
    box = _make_box(200, 100, 50, 50)
    box.layer = 2
    hit = raycast(Vector2(0, 100), Vector2(1, 0), [box], layer_mask=1)
    assert hit is None
    hit2 = raycast(Vector2(0, 100), Vector2(1, 0), [box], layer_mask=2)
    assert hit2 is not None

def test_raycast_closest():
    a = _make_box(100, 100, 50, 50)
    b = _make_box(300, 100, 50, 50)
    hit = raycast(Vector2(0, 100), Vector2(1, 0), [a, b])
    assert hit.collider is a

def test_raycast_all_sorted():
    a = _make_box(100, 100, 50, 50)
    b = _make_box(300, 100, 50, 50)
    hits = raycast_all(Vector2(0, 100), Vector2(1, 0), [b, a])
    assert len(hits) == 2
    assert hits[0].distance < hits[1].distance
