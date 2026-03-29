"""Tests for engine.math module."""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from engine.math.vector2 import Vector2
from engine.math.rect import Rect
from engine.math.circle import Circle
from engine.math.transform import Transform2D
from engine.math.utils import lerp, clamp, remap, inverse_lerp, smoothstep
from engine.math.easing import EASINGS, ease_out_bounce, linear


# --- Vector2 ---

def test_vector2_add():
    assert Vector2(1, 2) + Vector2(3, 4) == Vector2(4, 6)

def test_vector2_sub():
    assert Vector2(5, 3) - Vector2(1, 2) == Vector2(4, 1)

def test_vector2_mul():
    assert Vector2(2, 3) * 2 == Vector2(4, 6)

def test_vector2_rmul():
    assert 3 * Vector2(1, 2) == Vector2(3, 6)

def test_vector2_div():
    assert Vector2(6, 4) / 2 == Vector2(3, 2)

def test_vector2_neg():
    assert -Vector2(1, -2) == Vector2(-1, 2)

def test_vector2_magnitude():
    v = Vector2(3, 4)
    assert abs(v.magnitude - 5.0) < 0.0001

def test_vector2_sqr_magnitude():
    v = Vector2(3, 4)
    assert v.sqr_magnitude == 25.0

def test_vector2_normalized():
    v = Vector2(0, 5).normalized
    assert abs(v.x) < 0.0001
    assert abs(v.y - 1.0) < 0.0001

def test_vector2_normalized_zero():
    v = Vector2.zero().normalized
    assert v == Vector2.zero()

def test_vector2_dot():
    assert Vector2(1, 0).dot(Vector2(0, 1)) == 0.0
    assert Vector2(1, 0).dot(Vector2(1, 0)) == 1.0

def test_vector2_cross():
    assert Vector2(1, 0).cross(Vector2(0, 1)) == 1.0

def test_vector2_distance():
    a = Vector2(0, 0)
    b = Vector2(3, 4)
    assert abs(a.distance_to(b) - 5.0) < 0.0001

def test_vector2_lerp():
    a = Vector2(0, 0)
    b = Vector2(10, 20)
    mid = a.lerp(b, 0.5)
    assert mid == Vector2(5, 10)

def test_vector2_rotate():
    v = Vector2(1, 0).rotate(90)
    assert abs(v.x) < 0.0001
    assert abs(v.y - 1.0) < 0.0001

def test_vector2_iter():
    x, y = Vector2(3, 7)
    assert x == 3.0 and y == 7.0

def test_vector2_index():
    v = Vector2(5, 9)
    assert v[0] == 5.0 and v[1] == 9.0

def test_vector2_static_constructors():
    assert Vector2.zero() == Vector2(0, 0)
    assert Vector2.one() == Vector2(1, 1)
    assert Vector2.up() == Vector2(0, -1)
    assert Vector2.right() == Vector2(1, 0)

def test_vector2_from_angle():
    v = Vector2.from_angle(0)
    assert abs(v.x - 1.0) < 0.0001
    assert abs(v.y) < 0.0001


# --- Rect ---

def test_rect_properties():
    r = Rect(10, 20, 100, 50)
    assert r.left == 10
    assert r.right == 110
    assert r.top == 20
    assert r.bottom == 70
    assert r.center == Vector2(60, 45)

def test_rect_contains_point():
    r = Rect(0, 0, 100, 100)
    assert r.contains_point(Vector2(50, 50))
    assert r.contains_point(Vector2(0, 0))
    assert not r.contains_point(Vector2(101, 50))

def test_rect_overlaps():
    a = Rect(0, 0, 100, 100)
    b = Rect(50, 50, 100, 100)
    c = Rect(200, 200, 50, 50)
    assert a.overlaps(b)
    assert not a.overlaps(c)

def test_rect_intersection():
    a = Rect(0, 0, 100, 100)
    b = Rect(50, 50, 100, 100)
    i = a.intersection(b)
    assert i is not None
    assert i == Rect(50, 50, 50, 50)

def test_rect_no_intersection():
    a = Rect(0, 0, 10, 10)
    b = Rect(20, 20, 10, 10)
    assert a.intersection(b) is None

def test_rect_expanded():
    r = Rect(10, 10, 20, 20).expanded(5)
    assert r == Rect(5, 5, 30, 30)


# --- Circle ---

def test_circle_contains_point():
    c = Circle(Vector2(0, 0), 10)
    assert c.contains_point(Vector2(5, 5))
    assert not c.contains_point(Vector2(10, 10))

def test_circle_overlaps_circle():
    a = Circle(Vector2(0, 0), 10)
    b = Circle(Vector2(15, 0), 10)
    c = Circle(Vector2(100, 0), 5)
    assert a.overlaps_circle(b)
    assert not a.overlaps_circle(c)

def test_circle_overlaps_rect():
    c = Circle(Vector2(0, 0), 10)
    r = Rect(5, -5, 20, 10)
    assert c.overlaps_rect(r)

def test_circle_bounds():
    c = Circle(Vector2(50, 50), 10)
    b = c.get_bounds()
    assert b == Rect(40, 40, 20, 20)


# --- Transform2D ---

def test_transform_defaults():
    t = Transform2D()
    assert t.position == Vector2.zero()
    assert t.rotation == 0.0
    assert t.scale == Vector2.one()

def test_transform_translate():
    t = Transform2D(position=Vector2(10, 20))
    t.translate(Vector2(5, -5))
    assert t.position == Vector2(15, 15)

def test_transform_look_at():
    t = Transform2D()
    t.look_at(Vector2(1, 0))
    assert abs(t.rotation - 0.0) < 0.0001


# --- utils ---

def test_lerp():
    assert lerp(0, 100, 0.5) == 50.0

def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-5, 0, 10) == 0
    assert clamp(15, 0, 10) == 10

def test_remap():
    assert abs(remap(5, 0, 10, 0, 100) - 50.0) < 0.0001

def test_inverse_lerp():
    assert abs(inverse_lerp(0, 100, 50) - 0.5) < 0.0001

def test_smoothstep():
    assert smoothstep(0, 1, 0) == 0.0
    assert smoothstep(0, 1, 1) == 1.0
    assert abs(smoothstep(0, 1, 0.5) - 0.5) < 0.0001


# --- Easing ---

def test_easing_count():
    assert len(EASINGS) == 28

def test_easing_boundaries():
    for name, fn in EASINGS.items():
        assert abs(fn(0.0)) < 0.1, f"{name}(0) should be near 0"
        assert abs(fn(1.0) - 1.0) < 0.1, f"{name}(1) should be near 1"

def test_linear_easing():
    assert linear(0.5) == 0.5
