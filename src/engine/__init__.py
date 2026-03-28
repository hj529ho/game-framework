"""A 2D game engine built on SDL2."""

from engine.core.lifecycle import Lifecycle
from engine.core.app import App, current_app
from engine.core.clock import Clock
from engine.core.game import Game

from engine.math.vector2 import Vector2
from engine.math.rect import Rect
from engine.math.circle import Circle
from engine.math.transform import Transform2D

from engine.input.keys import Key, MouseButton
from engine.input.keyboard import Keyboard
from engine.input.mouse import Mouse

from engine.renderer.renderer import Renderer
from engine.renderer.color import Color
from engine.renderer.sprite import SpriteRenderer
from engine.renderer.text import TextRenderer

from engine.ecs.entity import Entity
from engine.ecs.component import Component
from engine.ecs.world import World

from engine.scene.scene import Scene
from engine.scene.scene_manager import SceneManager

from engine.resources.resource_manager import ResourceManager
from engine.audio.audio import Sound, Music

__version__ = "0.1.0"

__all__ = [
    "Lifecycle", "App", "current_app", "Clock", "Game",
    "Vector2", "Rect", "Circle", "Transform2D",
    "Key", "MouseButton", "Keyboard", "Mouse",
    "Renderer", "Color", "SpriteRenderer", "TextRenderer",
    "Entity", "Component", "World",
    "Scene", "SceneManager",
    "ResourceManager", "Sound", "Music",
]
