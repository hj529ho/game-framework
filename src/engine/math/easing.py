"""Easing functions. All take t (0.0 ~ 1.0) and return eased value (0.0 ~ 1.0)."""

from __future__ import annotations

import math

# --- Linear ---

def linear(t: float) -> float:
    return t

# --- Quad ---

def ease_in_quad(t: float) -> float:
    return t * t

def ease_out_quad(t: float) -> float:
    return 1 - (1 - t) * (1 - t)

def ease_in_out_quad(t: float) -> float:
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2

# --- Cubic ---

def ease_in_cubic(t: float) -> float:
    return t * t * t

def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3

def ease_in_out_cubic(t: float) -> float:
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2

# --- Quart ---

def ease_in_quart(t: float) -> float:
    return t ** 4

def ease_out_quart(t: float) -> float:
    return 1 - (1 - t) ** 4

def ease_in_out_quart(t: float) -> float:
    return 8 * t ** 4 if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2

# --- Sine ---

def ease_in_sine(t: float) -> float:
    return 1 - math.cos(t * math.pi / 2)

def ease_out_sine(t: float) -> float:
    return math.sin(t * math.pi / 2)

def ease_in_out_sine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2

# --- Expo ---

def ease_in_expo(t: float) -> float:
    return 0.0 if t == 0 else 2 ** (10 * t - 10)

def ease_out_expo(t: float) -> float:
    return 1.0 if t == 1 else 1 - 2 ** (-10 * t)

def ease_in_out_expo(t: float) -> float:
    if t == 0:
        return 0.0
    if t == 1:
        return 1.0
    if t < 0.5:
        return 2 ** (20 * t - 10) / 2
    return (2 - 2 ** (-20 * t + 10)) / 2

# --- Circ ---

def ease_in_circ(t: float) -> float:
    return 1 - math.sqrt(1 - t * t)

def ease_out_circ(t: float) -> float:
    return math.sqrt(1 - (t - 1) ** 2)

def ease_in_out_circ(t: float) -> float:
    if t < 0.5:
        return (1 - math.sqrt(1 - (2 * t) ** 2)) / 2
    return (math.sqrt(1 - (-2 * t + 2) ** 2) + 1) / 2

# --- Back ---

def ease_in_back(t: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t * t * t - c1 * t * t

def ease_out_back(t: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def ease_in_out_back(t: float) -> float:
    c1 = 1.70158
    c2 = c1 * 1.525
    if t < 0.5:
        return ((2 * t) ** 2 * ((c2 + 1) * 2 * t - c2)) / 2
    return ((2 * t - 2) ** 2 * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2

# --- Elastic ---

def ease_in_elastic(t: float) -> float:
    if t == 0 or t == 1:
        return t
    c4 = (2 * math.pi) / 3
    return -(2 ** (10 * t - 10)) * math.sin((t * 10 - 10.75) * c4)

def ease_out_elastic(t: float) -> float:
    if t == 0 or t == 1:
        return t
    c4 = (2 * math.pi) / 3
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * c4) + 1

def ease_in_out_elastic(t: float) -> float:
    if t == 0 or t == 1:
        return t
    c5 = (2 * math.pi) / 4.5
    if t < 0.5:
        return -(2 ** (20 * t - 10) * math.sin((20 * t - 11.125) * c5)) / 2
    return (2 ** (-20 * t + 10) * math.sin((20 * t - 11.125) * c5)) / 2 + 1

# --- Bounce ---

def ease_out_bounce(t: float) -> float:
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375

def ease_in_bounce(t: float) -> float:
    return 1 - ease_out_bounce(1 - t)

def ease_in_out_bounce(t: float) -> float:
    if t < 0.5:
        return (1 - ease_out_bounce(1 - 2 * t)) / 2
    return (1 + ease_out_bounce(2 * t - 1)) / 2


# --- Lookup by name ---

EASINGS: dict[str, callable] = {
    "linear": linear,
    "ease_in_quad": ease_in_quad,
    "ease_out_quad": ease_out_quad,
    "ease_in_out_quad": ease_in_out_quad,
    "ease_in_cubic": ease_in_cubic,
    "ease_out_cubic": ease_out_cubic,
    "ease_in_out_cubic": ease_in_out_cubic,
    "ease_in_quart": ease_in_quart,
    "ease_out_quart": ease_out_quart,
    "ease_in_out_quart": ease_in_out_quart,
    "ease_in_sine": ease_in_sine,
    "ease_out_sine": ease_out_sine,
    "ease_in_out_sine": ease_in_out_sine,
    "ease_in_expo": ease_in_expo,
    "ease_out_expo": ease_out_expo,
    "ease_in_out_expo": ease_in_out_expo,
    "ease_in_circ": ease_in_circ,
    "ease_out_circ": ease_out_circ,
    "ease_in_out_circ": ease_in_out_circ,
    "ease_in_back": ease_in_back,
    "ease_out_back": ease_out_back,
    "ease_in_out_back": ease_in_out_back,
    "ease_in_elastic": ease_in_elastic,
    "ease_out_elastic": ease_out_elastic,
    "ease_in_out_elastic": ease_in_out_elastic,
    "ease_in_bounce": ease_in_bounce,
    "ease_out_bounce": ease_out_bounce,
    "ease_in_out_bounce": ease_in_out_bounce,
}
