"""Scene demo: Game scene + pause menu, switch with SPACE."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import engine


# --- Components ---

class Movement(engine.Component):
    def on_start(self):
        self.speed = 300.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        dx, dy = 0.0, 0.0
        if kb.is_pressed(engine.Key.LEFT):
            dx -= 1
        if kb.is_pressed(engine.Key.RIGHT):
            dx += 1
        if kb.is_pressed(engine.Key.UP):
            dy -= 1
        if kb.is_pressed(engine.Key.DOWN):
            dy += 1
        self.transform.translate(engine.Vector2(dx, dy) * self.speed * dt)


class SineWave(engine.Component):
    """Moves the entity in a sine wave pattern."""

    def on_start(self):
        self.timer = 0.0
        self.start_pos = self.position.copy()
        self.amplitude = 100.0
        self.frequency = 2.0

    def on_update(self, dt):
        self.timer += dt
        offset = engine.Vector2(math.sin(self.timer * self.frequency) * self.amplitude, 0)
        self.position = self.start_pos + offset


class BoxRenderer(engine.Component):
    def on_awake(self):
        self.color = engine.Color.BLUE
        self.size = 40

    def on_draw(self, renderer):
        p = self.position
        half = self.size / 2
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size, self.color)


class SceneController(engine.Component):
    """Handles scene transitions and quit."""

    def on_update(self, dt):
        app = engine.current_app()
        kb = app.keyboard

        if kb.is_just_pressed(engine.Key.ESCAPE):
            app.quit()

        if kb.is_just_pressed(engine.Key.SPACE):
            game = self.entity._world  # access world for scene manager
            # Push pause menu via the game's scene manager
            from engine.core.game import Game
            # We'll use a simpler approach: access the scene manager
            # through the current_app pattern
            pass  # scene transitions handled at scene level


# --- Scenes ---

class GameScene(engine.Scene):
    def on_enter(self):
        # Player
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 400)
        player.add_component(Movement())
        box = player.add_component(BoxRenderer())
        box.color = engine.Color.BLUE
        box.size = 50
        self.add(player)

        # Enemies
        for i in range(3):
            enemy = engine.Entity(f"Enemy_{i}")
            enemy.position = engine.Vector2(200 + i * 200, 150)
            enemy.add_component(SineWave())
            box = enemy.add_component(BoxRenderer())
            box.color = engine.Color.RED
            box.size = 30
            self.add(enemy)

    def on_exit(self):
        self.world.clear()

    def on_pause(self):
        print("Game paused")

    def on_resume(self):
        print("Game resumed")


class PauseScene(engine.Scene):
    def on_enter(self):
        overlay = engine.Entity("PauseOverlay")
        overlay.position = engine.Vector2(400, 300)
        box = overlay.add_component(BoxRenderer())
        box.color = engine.Color.GRAY
        box.size = 200
        self.add(overlay)

    def on_exit(self):
        self.world.clear()


# --- Custom Game with SPACE to toggle pause ---

game = engine.Game(title="Scene Demo - SPACE to pause", width=800, height=600)

# We need to handle scene switching in the game loop.
# Since Game.run() manages the loop, we'll use a component for this.

class PauseToggle(engine.Component):
    """Toggles pause scene via the game's scene manager."""

    def on_awake(self):
        self.game_ref = game

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        if kb.is_just_pressed(engine.Key.ESCAPE):
            engine.current_app().quit()

        if kb.is_just_pressed(engine.Key.SPACE):
            sm = self.game_ref.scenes
            if sm.stack_depth == 1:
                sm.push(PauseScene("pause"))
            else:
                sm.pop()


# Add the controller to the game scene
class MainScene(GameScene):
    def on_enter(self):
        super().on_enter()
        controller = engine.Entity("Controller")
        controller.add_component(PauseToggle())
        self.add(controller)


game.run(MainScene("game"))
