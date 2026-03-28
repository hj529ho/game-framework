from __future__ import annotations

import math
from dataclasses import dataclass

from engine.math.vector2 import Vector2
from engine.math.rect import Rect
from engine.math.circle import Circle
from engine.physics.collider import Collider, BoxCollider, CircleCollider


@dataclass
class CollisionInfo:
    """Result of a collision test between two colliders."""
    collider_a: Collider
    collider_b: Collider
    normal: Vector2        # push direction: pushes A away from B
    penetration: float     # overlap depth
    contact_point: Vector2 # approximate contact point


@dataclass
class RaycastHit:
    """Result of a raycast."""
    collider: Collider     # the collider that was hit
    point: Vector2         # world-space hit point
    normal: Vector2        # surface normal at hit point
    distance: float        # distance from ray origin to hit point


def test_collision(a: Collider, b: Collider) -> CollisionInfo | None:
    """Test collision between two colliders. Returns CollisionInfo or None."""
    if isinstance(a, BoxCollider) and isinstance(b, BoxCollider):
        return _aabb_vs_aabb(a, b)
    elif isinstance(a, CircleCollider) and isinstance(b, CircleCollider):
        return _circle_vs_circle(a, b)
    elif isinstance(a, BoxCollider) and isinstance(b, CircleCollider):
        return _aabb_vs_circle(a, b)
    elif isinstance(a, CircleCollider) and isinstance(b, BoxCollider):
        result = _aabb_vs_circle(b, a)
        if result:
            result.collider_a, result.collider_b = a, b
            result.normal = -result.normal
        return result
    return None


def _aabb_vs_aabb(a: BoxCollider, b: BoxCollider) -> CollisionInfo | None:
    ar = a.get_bounds()
    br = b.get_bounds()

    if not ar.overlaps(br):
        return None

    # Calculate overlap on each axis
    dx_right = ar.right - br.left
    dx_left = br.right - ar.left
    dy_down = ar.bottom - br.top
    dy_up = br.bottom - ar.top

    # Find minimum penetration axis
    min_overlap = dx_right
    normal = Vector2(-1, 0)

    if dx_left < min_overlap:
        min_overlap = dx_left
        normal = Vector2(1, 0)
    if dy_down < min_overlap:
        min_overlap = dy_down
        normal = Vector2(0, -1)
    if dy_up < min_overlap:
        min_overlap = dy_up
        normal = Vector2(0, 1)

    contact = (a.world_center + b.world_center) * 0.5
    return CollisionInfo(a, b, normal, min_overlap, contact)


def _circle_vs_circle(a: CircleCollider, b: CircleCollider) -> CollisionInfo | None:
    ca = a.world_center
    cb = b.world_center
    diff = ca - cb
    dist_sq = diff.sqr_magnitude
    radius_sum = a.radius + b.radius

    if dist_sq >= radius_sum * radius_sum:
        return None

    dist = math.sqrt(dist_sq)
    if dist == 0:
        normal = Vector2(1, 0)
        penetration = radius_sum
    else:
        normal = diff / dist
        penetration = radius_sum - dist

    contact = cb + normal * b.radius
    return CollisionInfo(a, b, normal, penetration, contact)


def _aabb_vs_circle(box: BoxCollider, circle: CircleCollider) -> CollisionInfo | None:
    rect = box.get_bounds()
    cc = circle.world_center

    # Find closest point on rect to circle center
    closest_x = max(rect.left, min(cc.x, rect.right))
    closest_y = max(rect.top, min(cc.y, rect.bottom))
    closest = Vector2(closest_x, closest_y)

    diff = cc - closest
    dist_sq = diff.sqr_magnitude

    if dist_sq >= circle.radius * circle.radius:
        return None

    dist = math.sqrt(dist_sq)
    if dist == 0:
        # Circle center inside the box — push out along shortest axis
        dx_right = rect.right - cc.x
        dx_left = cc.x - rect.left
        dy_down = rect.bottom - cc.y
        dy_up = cc.y - rect.top

        min_d = dx_right
        normal = Vector2(1, 0)
        if dx_left < min_d:
            min_d = dx_left
            normal = Vector2(-1, 0)
        if dy_down < min_d:
            min_d = dy_down
            normal = Vector2(0, 1)
        if dy_up < min_d:
            min_d = dy_up
            normal = Vector2(0, -1)
        penetration = circle.radius + min_d
    else:
        normal = diff / dist
        penetration = circle.radius - dist

    contact = closest
    return CollisionInfo(box, circle, -normal, penetration, contact)


# ---------------------------------------------------------------------------
# Raycast
# ---------------------------------------------------------------------------

def raycast(
    origin: Vector2,
    direction: Vector2,
    colliders: list[Collider],
    max_distance: float = float('inf'),
    layer_mask: int = 0xFFFFFFFF,
) -> RaycastHit | None:
    """Cast a ray and return the closest hit, or None.

    Args:
        origin: Ray start point in world space.
        direction: Ray direction (will be normalized).
        colliders: List of colliders to test against.
        max_distance: Maximum ray length.
        layer_mask: Bitmask; only test colliders whose layer & mask is truthy.

    Returns:
        RaycastHit for the closest collider hit, or None.
    """
    d = direction.normalized
    if d.sqr_magnitude == 0:
        return None

    closest: RaycastHit | None = None

    for col in colliders:
        if not (col.layer & layer_mask):
            continue

        hit: RaycastHit | None = None
        if isinstance(col, BoxCollider):
            hit = _ray_vs_aabb(origin, d, max_distance, col)
        elif isinstance(col, CircleCollider):
            hit = _ray_vs_circle(origin, d, max_distance, col)

        if hit and (closest is None or hit.distance < closest.distance):
            closest = hit

    return closest


def raycast_all(
    origin: Vector2,
    direction: Vector2,
    colliders: list[Collider],
    max_distance: float = float('inf'),
    layer_mask: int = 0xFFFFFFFF,
) -> list[RaycastHit]:
    """Cast a ray and return all hits sorted by distance."""
    d = direction.normalized
    if d.sqr_magnitude == 0:
        return []

    hits: list[RaycastHit] = []
    for col in colliders:
        if not (col.layer & layer_mask):
            continue

        hit: RaycastHit | None = None
        if isinstance(col, BoxCollider):
            hit = _ray_vs_aabb(origin, d, max_distance, col)
        elif isinstance(col, CircleCollider):
            hit = _ray_vs_circle(origin, d, max_distance, col)

        if hit:
            hits.append(hit)

    hits.sort(key=lambda h: h.distance)
    return hits


def _ray_vs_aabb(origin: Vector2, d: Vector2, max_dist: float, box: BoxCollider) -> RaycastHit | None:
    rect = box.get_bounds()

    # Slab method
    if d.x != 0:
        t1 = (rect.left - origin.x) / d.x
        t2 = (rect.right - origin.x) / d.x
    else:
        t1 = float('-inf') if rect.left <= origin.x else float('inf')
        t2 = float('inf') if rect.right >= origin.x else float('-inf')

    if t1 > t2:
        t1, t2 = t2, t1
    tmin, tmax = t1, t2

    if d.y != 0:
        t1 = (rect.top - origin.y) / d.y
        t2 = (rect.bottom - origin.y) / d.y
    else:
        t1 = float('-inf') if rect.top <= origin.y else float('inf')
        t2 = float('inf') if rect.bottom >= origin.y else float('-inf')

    if t1 > t2:
        t1, t2 = t2, t1

    tmin = max(tmin, t1)
    tmax = min(tmax, t2)

    if tmax < 0 or tmin > tmax or tmin > max_dist:
        return None

    t = tmin if tmin >= 0 else tmax
    if t < 0 or t > max_dist:
        return None

    point = origin + d * t

    # Determine normal from which face was hit
    eps = 0.001
    if abs(point.x - rect.left) < eps:
        normal = Vector2(-1, 0)
    elif abs(point.x - rect.right) < eps:
        normal = Vector2(1, 0)
    elif abs(point.y - rect.top) < eps:
        normal = Vector2(0, -1)
    else:
        normal = Vector2(0, 1)

    return RaycastHit(box, point, normal, t)


def _ray_vs_circle(origin: Vector2, d: Vector2, max_dist: float, circle: CircleCollider) -> RaycastHit | None:
    cc = circle.world_center
    r = circle.radius

    oc = origin - cc
    a = d.dot(d)  # always 1 if normalized, but keep general
    b = 2.0 * oc.dot(d)
    c = oc.dot(oc) - r * r

    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return None

    sqrt_disc = math.sqrt(discriminant)
    t1 = (-b - sqrt_disc) / (2 * a)
    t2 = (-b + sqrt_disc) / (2 * a)

    t = t1 if t1 >= 0 else t2
    if t < 0 or t > max_dist:
        return None

    point = origin + d * t
    normal = (point - cc).normalized

    return RaycastHit(circle, point, normal, t)
