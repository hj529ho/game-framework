"""Tests for engine.animation and engine.tween modules."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from engine.animation.clip import AnimationClip
from engine.animation.state_machine import AnimatorStateMachine
from engine.tween.tween import Tween, TweenSequence, TweenParallel, TweenManager, LoopType
from engine.tween import tween as tween_mod
from engine.ecs.entity import Entity
from engine.math.vector2 import Vector2


def _make_tween_env():
    """Create entity + TweenManager, reset global manager."""
    tween_mod._global_manager = None
    e = Entity()
    e.position = Vector2(0, 0)
    mgr = e.add_component(TweenManager())
    return e, mgr


# --- AnimationClip ---

def test_clip_basics():
    clip = AnimationClip("walk", [0, 1, 2, 3], fps=10)
    assert clip.frame_count == 4
    assert clip.duration == 0.4

def test_clip_events():
    fired = []
    clip = AnimationClip("attack", [0, 1, 2], fps=10, loop=False)
    clip.add_event(1, lambda: fired.append("hit"))
    assert len(clip.events) == 1


# --- AnimatorStateMachine ---

def test_state_machine_play():
    sm = AnimatorStateMachine()
    sm.add_state("idle", AnimationClip("idle", [0, 1], fps=8))
    sm.play("idle")
    assert sm.current_state == "idle"

def test_state_machine_transition():
    sm = AnimatorStateMachine()
    sm.add_state("idle", AnimationClip("idle", [0, 1], fps=8))
    sm.add_state("run", AnimationClip("run", [2, 3, 4], fps=12))
    sm.set_param("speed", 0.0)
    sm.add_transition("idle", "run", condition=lambda p: p["speed"] > 0)
    sm.add_transition("run", "idle", condition=lambda p: p["speed"] <= 0)

    sm.play("idle")
    sm.set_param("speed", 5.0)
    sm.update(0.1)
    assert sm.current_state == "run"

    sm.set_param("speed", 0.0)
    sm.update(0.1)
    assert sm.current_state == "idle"

def test_state_machine_exit_time():
    sm = AnimatorStateMachine()
    sm.add_state("attack", AnimationClip("attack", [0, 1, 2], fps=10, loop=False))
    sm.add_state("idle", AnimationClip("idle", [0, 1], fps=8))
    sm.add_transition("attack", "idle", exit_time=1.0)

    sm.play("attack")
    sm.update(0.1)
    assert sm.current_state == "attack"

    for _ in range(20):
        sm.update(1 / 10)
    assert sm.current_state == "idle"

def test_state_machine_wildcard():
    sm = AnimatorStateMachine()
    sm.add_state("idle", AnimationClip("idle", [0], fps=8))
    sm.add_state("hurt", AnimationClip("hurt", [0], fps=8))
    sm.set_param("hit", False)
    sm.add_transition("*", "hurt", condition=lambda p: p["hit"])

    sm.play("idle")
    sm.set_param("hit", True)
    sm.update(0.1)
    assert sm.current_state == "hurt"

def test_state_machine_frame_events():
    fired = []
    clip = AnimationClip("attack", [0, 1, 2], fps=10, loop=False)
    clip.add_event(1, lambda: fired.append("hit"))

    sm = AnimatorStateMachine()
    sm.add_state("attack", clip)
    sm.play("attack")

    for _ in range(10):
        sm.update(1 / 10)

    assert "hit" in fired

def test_state_machine_params():
    sm = AnimatorStateMachine()
    sm.set_param("speed", 5.0)
    assert sm.get_param("speed") == 5.0


# --- Tween ---

def test_tween_basic():
    e, mgr = _make_tween_env()
    Tween.move(e, Vector2(100, 0), 1.0).set_ease("linear").play()
    for _ in range(10):
        mgr.on_update(0.1)
    assert abs(e.position.x - 100.0) < 1.0

def test_tween_from_to():
    e, mgr = _make_tween_env()
    val = [0.0]
    Tween.from_to(lambda v: val.__setitem__(0, v), 0.0, 50.0, 0.5).set_ease("linear").play()
    for _ in range(5):
        mgr.on_update(0.1)
    assert abs(val[0] - 50.0) < 1.0

def test_tween_on_complete():
    e, mgr = _make_tween_env()
    done = []
    Tween.move(e, Vector2(10, 0), 0.3).on_complete(lambda: done.append(True)).play()
    for _ in range(10):
        mgr.on_update(0.1)
    assert len(done) == 1

def test_tween_delay():
    e, mgr = _make_tween_env()
    Tween.move(e, Vector2(100, 0), 0.5).set_delay(0.5).set_ease("linear").play()
    for _ in range(5):
        mgr.on_update(0.1)
    assert abs(e.position.x) < 5.0  # still in delay
    for _ in range(5):
        mgr.on_update(0.1)
    assert e.position.x > 50.0  # started moving

def test_tween_sequence():
    e, mgr = _make_tween_env()
    seq = TweenSequence()
    seq.append(Tween.move(e, Vector2(50, 0), 0.2))
    seq.append_interval(0.1)
    seq.append(Tween.move(e, Vector2(50, 50), 0.2))
    seq.play()
    for _ in range(10):
        mgr.on_update(0.1)
    assert abs(e.position.y - 50.0) < 10.0

def test_tween_parallel():
    e, mgr = _make_tween_env()
    par = TweenParallel()
    par.add(Tween.move(e, Vector2(100, 0), 0.5))
    par.add(Tween.rotate_to(e, 90, 0.5))
    par.play()
    for _ in range(10):
        mgr.on_update(0.1)
    assert e.position.x > 50.0
    assert e.rotation > 45.0

def test_tween_kill():
    e, mgr = _make_tween_env()
    tw = Tween.move(e, Vector2(1000, 0), 10.0).set_ease("linear").play()
    mgr.on_update(0.1)
    tw.kill()
    old_x = e.position.x
    mgr.on_update(0.1)
    assert e.position.x == old_x
