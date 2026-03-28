from __future__ import annotations

from enum import IntEnum

from sdl2 import (
    SDLK_a, SDLK_b, SDLK_c, SDLK_d, SDLK_e, SDLK_f, SDLK_g, SDLK_h,
    SDLK_i, SDLK_j, SDLK_k, SDLK_l, SDLK_m, SDLK_n, SDLK_o, SDLK_p,
    SDLK_q, SDLK_r, SDLK_s, SDLK_t, SDLK_u, SDLK_v, SDLK_w, SDLK_x,
    SDLK_y, SDLK_z,
    SDLK_0, SDLK_1, SDLK_2, SDLK_3, SDLK_4, SDLK_5, SDLK_6, SDLK_7,
    SDLK_8, SDLK_9,
    SDLK_UP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT,
    SDLK_SPACE, SDLK_RETURN, SDLK_ESCAPE, SDLK_TAB, SDLK_BACKSPACE,
    SDLK_DELETE,
    SDLK_LSHIFT, SDLK_RSHIFT, SDLK_LCTRL, SDLK_RCTRL, SDLK_LALT, SDLK_RALT,
    SDLK_F1, SDLK_F2, SDLK_F3, SDLK_F4, SDLK_F5, SDLK_F6,
    SDLK_F7, SDLK_F8, SDLK_F9, SDLK_F10, SDLK_F11, SDLK_F12,
    SDL_BUTTON_LEFT, SDL_BUTTON_MIDDLE, SDL_BUTTON_RIGHT,
)


class Key(IntEnum):
    # Letters
    A = SDLK_a
    B = SDLK_b
    C = SDLK_c
    D = SDLK_d
    E = SDLK_e
    F = SDLK_f
    G = SDLK_g
    H = SDLK_h
    I = SDLK_i
    J = SDLK_j
    K = SDLK_k
    L = SDLK_l
    M = SDLK_m
    N = SDLK_n
    O = SDLK_o
    P = SDLK_p
    Q = SDLK_q
    R = SDLK_r
    S = SDLK_s
    T = SDLK_t
    U = SDLK_u
    V = SDLK_v
    W = SDLK_w
    X = SDLK_x
    Y = SDLK_y
    Z = SDLK_z

    # Numbers
    NUM_0 = SDLK_0
    NUM_1 = SDLK_1
    NUM_2 = SDLK_2
    NUM_3 = SDLK_3
    NUM_4 = SDLK_4
    NUM_5 = SDLK_5
    NUM_6 = SDLK_6
    NUM_7 = SDLK_7
    NUM_8 = SDLK_8
    NUM_9 = SDLK_9

    # Arrows
    UP = SDLK_UP
    DOWN = SDLK_DOWN
    LEFT = SDLK_LEFT
    RIGHT = SDLK_RIGHT

    # Special
    SPACE = SDLK_SPACE
    RETURN = SDLK_RETURN
    ESCAPE = SDLK_ESCAPE
    TAB = SDLK_TAB
    BACKSPACE = SDLK_BACKSPACE
    DELETE = SDLK_DELETE

    # Modifiers
    LSHIFT = SDLK_LSHIFT
    RSHIFT = SDLK_RSHIFT
    LCTRL = SDLK_LCTRL
    RCTRL = SDLK_RCTRL
    LALT = SDLK_LALT
    RALT = SDLK_RALT

    # Function keys
    F1 = SDLK_F1
    F2 = SDLK_F2
    F3 = SDLK_F3
    F4 = SDLK_F4
    F5 = SDLK_F5
    F6 = SDLK_F6
    F7 = SDLK_F7
    F8 = SDLK_F8
    F9 = SDLK_F9
    F10 = SDLK_F10
    F11 = SDLK_F11
    F12 = SDLK_F12


class MouseButton(IntEnum):
    LEFT = SDL_BUTTON_LEFT
    MIDDLE = SDL_BUTTON_MIDDLE
    RIGHT = SDL_BUTTON_RIGHT
