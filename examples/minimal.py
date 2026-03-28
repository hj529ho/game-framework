"""Minimal example: Entity with movement and rendering components."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import engine


# --- Components ---

class Movement(engine.Component):
    """Handles keyboard movement."""

    def on_start(self):
        self.speed = 300.0

    def on_update(self, dt):
        app = engine.current_app()
        kb = app.keyboard
        dx, dy = 0.0, 0.0
        if kb.is_pressed(engine.Key.LEFT) or kb.is_pressed(engine.Key.A):
            dx -= 1
        if kb.is_pressed(engine.Key.RIGHT) or kb.is_pressed(engine.Key.D):
            dx += 1
        if kb.is_pressed(engine.Key.UP) or kb.is_pressed(engine.Key.W):
            dy -= 1
        if kb.is_pressed(engine.Key.DOWN) or kb.is_pressed(engine.Key.S):
            dy += 1

        self.transform.translate(engine.Vector2(dx, dy) * self.speed * dt)


class BoxRenderer(engine.Component):
    """Draws a colored rectangle at the entity's position."""

    def on_awake(self):
        self.color = engine.Color.BLUE
        self.width = 50
        self.height = 50

    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(
            p.x - self.width / 2, p.y - self.height / 2,
            self.width, self.height,
            self.color,
        )


class QuitOnEscape(engine.Component):
    """Quits the game when Escape is pressed."""

    def on_update(self, dt):
        if engine.current_app().keyboard.is_just_pressed(engine.Key.ESCAPE):
            engine.current_app().quit()


# --- Scene ---

class GameScene(engine.Scene):
    def on_enter(self):
        # Player
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_component(Movement())
        player.add_component(BoxRenderer())
        player.add_component(QuitOnEscape())
        self.add(player)

        # Static obstacle
        obstacle = engine.Entity("Obstacle")
        obstacle.position = engine.Vector2(200, 200)
        box = obstacle.add_component(BoxRenderer())
        box.color = engine.Color.RED
        box.width = 40
        box.height = 40
        self.add(obstacle)


# --- Run ---

game = engine.Game(title="Minimal - Component Pattern", width=800, height=600)
game.run(GameScene())
