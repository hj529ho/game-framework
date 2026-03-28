"""A 2D game engine built on SDL2."""

from engine.core.lifecycle import Lifecycle
from engine.core.app import App, current_app
from engine.core.clock import Clock
from engine.core.game import Game
from engine.core.events import Event, EventBus, get_event_bus

from engine.math.vector2 import Vector2
from engine.math.rect import Rect
from engine.math.circle import Circle
from engine.math.transform import Transform2D
from engine.math.easing import EASINGS

from engine.input.keys import Key, MouseButton
from engine.input.keyboard import Keyboard
from engine.input.mouse import Mouse

from engine.renderer.renderer import Renderer
from engine.renderer.color import Color
from engine.renderer.sprite import SpriteRenderer
from engine.renderer.text import TextRenderer
from engine.renderer.camera import Camera2D
from engine.renderer.animated_sprite import AnimatedSprite, Animation

from engine.ecs.entity import Entity
from engine.ecs.component import Component
from engine.ecs.world import World

from engine.scene.scene import Scene
from engine.scene.scene_manager import SceneManager
from engine.scene.transition import Transition, FadeTransition, SlideTransition

from engine.resources.resource_manager import ResourceManager
from engine.audio.audio import Sound, Music

from engine.physics.collider import Collider, BoxCollider, CircleCollider
from engine.physics.collision import CollisionInfo, RaycastHit, test_collision, raycast, raycast_all
from engine.physics.physics_world import PhysicsWorld

from engine.animation.clip import AnimationClip, FrameEvent
from engine.animation.state_machine import AnimatorStateMachine
from engine.animation.animator import Animator

from engine.tween.tween import Tween, TweenSequence, TweenParallel, TweenManager, LoopType

__version__ = "0.1.0"

__all__ = [
    "Lifecycle", "App", "current_app", "Clock", "Game",
    "Event", "EventBus", "get_event_bus",
    "Vector2", "Rect", "Circle", "Transform2D", "EASINGS",
    "Key", "MouseButton", "Keyboard", "Mouse",
    "Renderer", "Color", "SpriteRenderer", "TextRenderer",
    "Camera2D", "AnimatedSprite", "Animation",
    "Entity", "Component", "World",
    "Scene", "SceneManager",
    "Transition", "FadeTransition", "SlideTransition",
    "ResourceManager", "Sound", "Music",
    "Collider", "BoxCollider", "CircleCollider",
    "CollisionInfo", "RaycastHit",
    "test_collision", "raycast", "raycast_all", "PhysicsWorld",
    "AnimationClip", "FrameEvent", "AnimatorStateMachine", "Animator",
    "Tween", "TweenSequence", "TweenParallel", "TweenManager", "LoopType",
]
