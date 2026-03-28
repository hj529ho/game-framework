from __future__ import annotations


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(value, max_val))


def remap(value: float, from_min: float, from_max: float,
          to_min: float, to_max: float) -> float:
    t = (value - from_min) / (from_max - from_min)
    return to_min + t * (to_max - to_min)


def inverse_lerp(a: float, b: float, value: float) -> float:
    if a == b:
        return 0.0
    return (value - a) / (b - a)


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)
