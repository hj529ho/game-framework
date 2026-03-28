# 씬 관리 (scene)

씬(Scene) 모듈은 게임의 화면 전환을 관리한다. 타이틀 화면, 게임 플레이 화면, 일시정지 메뉴, 게임 오버 화면 등을 각각 독립된 `Scene`으로 만들고, `SceneManager`의 스택 기반 전환으로 화면 간 이동을 구현한다. `Game.run()`이 초기 씬을 받아 게임 루프를 시작한다.

```python
from engine import Scene, SceneManager
```

---

## Scene

`Scene`은 하나의 `World`를 소유한다. World 안에 엔티티들이 존재하므로, 하나의 씬 = 하나의 게임 화면이라고 생각하면 된다.

### 구조

```
Scene
+-- name (str)           씬 이름 (기본: 클래스 이름)
+-- world (World)        엔티티 컨테이너
+-- 생명주기 훅:
|   +-- on_enter()       씬 활성화 시
|   +-- on_exit()        씬 제거 시
|   +-- on_pause()       위에 다른 씬이 올라올 때
|   +-- on_resume()      위의 씬이 제거될 때
+-- 프레임 메서드:
    +-- update(dt)       world.update(dt) 호출
    +-- draw(renderer)   world.draw(renderer) 호출
```

### 생성과 기본 사용

```python
import engine

# 서브클래스로 사용 (권장)
class GameScene(engine.Scene):
    def on_enter(self):
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_component(PlayerMovement())
        player.add_component(PlayerRenderer())
        self.add(player)

    def on_exit(self):
        self.world.clear()

# Game.run()에 초기 씬을 전달
game = engine.Game(title="My Game", width=800, height=600)
game.run(GameScene())
```

### Entity 편의 메서드

Scene은 `self.world`에 위임하는 편의 메서드를 제공한다.

```python
# 아래 두 줄은 동일하다
scene.add(entity)                      # 편의 메서드
scene.world.add(entity)                # 직접 호출

scene.remove(entity)                   # = scene.world.remove(entity)
scene.find("Player")                   # = scene.world.find_by_name("Player")
scene.find_by_tag("enemy")             # = scene.world.find_by_tag("enemy")
scene.find_with_component(Health)      # = scene.world.find_with_component(Health)
```

### 생명주기 훅

| 훅 | 호출 시점 | 용도 |
|---|---|---|
| `on_enter()` | 씬이 활성화될 때 (push, replace) | 엔티티 생성, 리소스 로드 |
| `on_exit()` | 씬이 스택에서 제거될 때 (pop, replace, clear) | 엔티티 정리, 리소스 해제 |
| `on_pause()` | 다른 씬이 위에 올라올 때 (push) | 게임 일시정지, 사운드 중단 |
| `on_resume()` | 위의 씬이 제거될 때 (pop) | 게임 재개, 사운드 재시작 |

```python
class GameScene(engine.Scene):
    def on_enter(self):
        print("게임 시작! 엔티티 생성 중...")
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_component(PlayerMovement())
        player.add_component(PlayerRenderer())
        self.add(player)

        for i in range(10):
            enemy = engine.Entity(f"Enemy_{i}")
            enemy.add_component(EnemyAI())
            enemy.add_component(EnemyRenderer())
            self.add(enemy)

    def on_pause(self):
        print("게임 일시정지 (메뉴가 올라옴)")

    def on_resume(self):
        print("게임 재개 (메뉴가 닫힘)")

    def on_exit(self):
        print("게임 종료. 정리 중...")
        self.world.clear()
```

### 프레임 메서드

`update`와 `draw`는 내부적으로 `self.world`의 동일 메서드를 호출한다. `Game.run()`이 매 프레임 이들을 자동으로 호출한다. 필요하면 오버라이드하여 추가 로직을 넣을 수 있다.

```python
class GameScene(engine.Scene):
    def update(self, dt):
        # 기본 엔티티 업데이트
        super().update(dt)

        # 추가 로직: 승리 조건 체크
        enemies = self.find_by_tag("enemy")
        if len(enemies) == 0:
            print("모든 적 처치! 승리!")

    def draw(self, renderer):
        # 기본 엔티티 그리기
        super().draw(renderer)

        # 추가: 씬 고유의 UI 그리기
        renderer.draw_rect(10, 10, 200, 20, engine.Color.DARK_GRAY, layer=10)
```

---

## SceneManager

`SceneManager`는 씬을 **스택(Stack)**으로 관리한다. 항상 스택 최상위(top)의 씬만 활성 상태이며, `update`와 `draw`의 대상이 된다. `Game`이 내부적으로 SceneManager를 소유하며 `game.scenes`로 접근할 수 있다.

### 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `current` | `Scene \| None` | 현재 활성 씬 (스택 최상위). 비어있으면 `None` |
| `stack_depth` | `int` | 스택에 있는 씬의 수 |

### 전환 메서드

모든 전환은 **지연(deferred)**된다. 즉시 실행되지 않고 대기열에 추가되며, `process_pending()` 또는 `update()` 끝에 일괄 처리된다.

#### push (씬 추가)

```python
game.scenes.push(PauseScene())
```

새 씬을 스택 위에 올린다. 이전 활성 씬은 `on_pause()`가 호출되고, 새 씬은 `on_enter()`가 호출된다.

#### pop (씬 제거)

```python
game.scenes.pop()
```

최상위 씬을 스택에서 제거한다. 제거되는 씬은 `on_exit()`가 호출되고, 아래의 씬은 `on_resume()`이 호출된다.

#### replace (씬 교체)

```python
game.scenes.replace(NewScene())
```

최상위 씬을 새 씬으로 교체한다. 이전 씬에 `on_exit()`, 새 씬에 `on_enter()`가 호출된다.

#### clear (전체 제거)

```python
game.scenes.clear()
```

스택의 모든 씬을 제거한다. 위에서부터 순서대로(LIFO) 각 씬의 `on_exit()`가 호출된다.

### process_pending

```python
game.scenes.process_pending()
```

대기 중인 전환을 즉시 처리한다. `Game.run()` 내부에서 매 프레임 자동으로 호출되므로, 보통은 직접 호출할 필요가 없다.

> **참고**: `Game.run()`이 시작 시 첫 번째 씬을 push하고 `process_pending()`을 호출하여 `on_enter()`를 실행한다. 개발자가 직접 이 과정을 관리할 필요가 없다.

### Component에서 씬 전환하기

Component에서 씬을 전환하려면 `game` 인스턴스의 `scenes` 속성에 접근해야 한다. 가장 일반적인 방법은 Component에 game 참조를 전달하거나, 전역 변수를 사용하는 것이다.

```python
class PauseToggle(engine.Component):
    """SPACE 키로 일시정지를 토글하는 컴포넌트."""

    def on_awake(self):
        self.game_ref = None  # 외부에서 설정

    def on_update(self, dt):
        kb = engine.current_app().keyboard

        if kb.is_just_pressed(engine.Key.ESCAPE):
            engine.current_app().quit()

        if kb.is_just_pressed(engine.Key.SPACE):
            sm = self.game_ref.scenes
            if sm.stack_depth == 1:
                sm.push(PauseScene())
            else:
                sm.pop()
```

---

## 씬 스택 동작 다이어그램

### push 동작

```
push(A):
                                     +---+
  스택: []                  스택: | A |
                                     +---+
  호출: A.on_enter()

push(B):
           +---+                     +---+
  스택: | A |            스택: | B |
           +---+                     +---+
                                     | A |
                                     +---+
  호출: A.on_pause(), B.on_enter()

push(C):
           +---+                     +---+
  스택: | B |            스택: | C |
           +---+                     +---+
           | A |                     | B |
           +---+                     +---+
                                     | A |
                                     +---+
  호출: B.on_pause(), C.on_enter()
```

### pop 동작

```
pop():  (C를 제거)
           +---+                     +---+
  스택: | C |            스택: | B |
           +---+                     +---+
           | B |                     | A |
           +---+                     +---+
           | A |
           +---+
  호출: C.on_exit(), B.on_resume()
```

### replace 동작

```
replace(D):  (B를 D로 교체)
           +---+                     +---+
  스택: | B |            스택: | D |
           +---+                     +---+
           | A |                     | A |
           +---+                     +---+
  호출: B.on_exit(), D.on_enter()
```

### clear 동작

```
clear():  (모든 씬 제거)
           +---+
  스택: | D |            스택: []
           +---+
           | A |
           +---+
  호출: D.on_exit(), A.on_exit()  (LIFO 순서)
```

### 전체 흐름 예시

```
초기 상태: []

push(Title)    -> [Title]          Title.on_enter()
push(Game)     -> [Title, Game]    Title.on_pause(), Game.on_enter()
push(Pause)    -> [Title, Game, Pause]  Game.on_pause(), Pause.on_enter()
pop()          -> [Title, Game]    Pause.on_exit(), Game.on_resume()
replace(Over)  -> [Title, Over]    Game.on_exit(), Over.on_enter()
pop()          -> [Title]          Over.on_exit(), Title.on_resume()
clear()        -> []               Title.on_exit()
```

---

## 일반적인 패턴

### 1. 타이틀 화면 -> 게임 -> 게임 오버

```python
import engine

# --- Components ---

class TitleUI(engine.Component):
    """타이틀 화면의 UI를 그리는 컴포넌트."""

    def on_draw(self, renderer):
        renderer.draw_rect(250, 200, 300, 60, engine.Color.WHITE, filled=False)
        renderer.draw_rect(300, 350, 200, 40, engine.Color.YELLOW, filled=False)


class SceneTransitioner(engine.Component):
    """씬 전환을 처리하는 컴포넌트."""

    def on_awake(self):
        self.game_ref = None  # 외부에서 설정

    def on_update(self, dt):
        kb = engine.current_app().keyboard

        if kb.is_just_pressed(engine.Key.ESCAPE):
            engine.current_app().quit()

        if kb.is_just_pressed(engine.Key.RETURN):
            self.game_ref.scenes.replace(GameScene(self.game_ref))


# --- Scenes ---

class TitleScene(engine.Scene):
    def __init__(self, game_ref):
        super().__init__()
        self.game_ref = game_ref

    def on_enter(self):
        ui = engine.Entity("TitleUI")
        ui.add_component(TitleUI())
        trans = ui.add_component(SceneTransitioner())
        trans.game_ref = self.game_ref
        self.add(ui)

    def on_exit(self):
        self.world.clear()


class GameScene(engine.Scene):
    def __init__(self, game_ref):
        super().__init__()
        self.game_ref = game_ref

    def on_enter(self):
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_tag("player")
        player.add_component(PlayerMovement())
        player.add_component(PlayerRenderer())
        self.add(player)

    def on_exit(self):
        self.world.clear()
```

### 2. 일시정지 메뉴 (오버레이)

```python
class PauseOverlay(engine.Component):
    """반투명 일시정지 화면을 그리는 컴포넌트."""

    def on_draw(self, renderer):
        # 반투명 배경
        renderer.draw_rect(0, 0, 800, 600, engine.Color(0, 0, 0, 128), layer=50)
        # 메뉴 박스
        renderer.draw_rect(250, 150, 300, 300, engine.Color.DARK_GRAY, layer=51)
        renderer.draw_rect(250, 150, 300, 300, engine.Color.WHITE, filled=False, layer=51)


class PauseMenu(engine.Component):
    """일시정지 메뉴 탐색을 처리하는 컴포넌트."""

    def on_start(self):
        self.options = ["계속하기", "설정", "타이틀로"]
        self.selected = 0

    def on_update(self, dt):
        kb = engine.current_app().keyboard

        if kb.is_just_pressed(engine.Key.UP):
            self.selected = (self.selected - 1) % len(self.options)
        if kb.is_just_pressed(engine.Key.DOWN):
            self.selected = (self.selected + 1) % len(self.options)

    def on_draw(self, renderer):
        for i, option in enumerate(self.options):
            y = 200 + i * 50
            if i == self.selected:
                renderer.draw_rect(270, y, 260, 30, engine.Color(80, 80, 120), layer=52)
            renderer.draw_rect(280, y + 5, 240, 20, engine.Color.WHITE, filled=False, layer=52)


class PauseScene(engine.Scene):
    def on_enter(self):
        pause_entity = engine.Entity("PauseMenu")
        pause_entity.add_component(PauseOverlay())
        pause_entity.add_component(PauseMenu())
        self.add(pause_entity)

    def on_exit(self):
        self.world.clear()
```

### 3. 여러 씬을 사용하는 전체 예제

```python
import engine
import random

# --- Components ---

class Health(engine.Component):
    def on_awake(self):
        self.hp = 100
        self.max_hp = 100

    def damage(self, amount):
        self.hp = max(0, self.hp - amount)

    @property
    def ratio(self):
        return self.hp / self.max_hp

    @property
    def is_alive(self):
        return self.hp > 0


class PlayerMovement(engine.Component):
    def on_start(self):
        self.speed = 200.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        direction = engine.Vector2.zero()
        if kb.is_pressed(engine.Key.W): direction = direction + engine.Vector2.up()
        if kb.is_pressed(engine.Key.S): direction = direction + engine.Vector2.down()
        if kb.is_pressed(engine.Key.A): direction = direction + engine.Vector2.left()
        if kb.is_pressed(engine.Key.D): direction = direction + engine.Vector2.right()
        if direction.magnitude > 0:
            self.transform.translate(direction.normalized * self.speed * dt)


class PlayerRenderer(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(p.x - 16, p.y - 16, 32, 32, engine.Color.BLUE)
        hp = self.entity.get_component(Health)
        if hp:
            renderer.draw_rect(p.x - 20, p.y - 24, 40, 4, engine.Color.RED, layer=1)
            renderer.draw_rect(p.x - 20, p.y - 24, 40 * hp.ratio, 4, engine.Color.GREEN, layer=1)


class EnemyAI(engine.Component):
    def on_start(self):
        self.speed = 60.0

    def on_update(self, dt):
        targets = self.entity._world.find_by_tag("player")
        if not targets:
            return
        target = targets[0]
        to_target = target.position - self.position
        if to_target.magnitude > 20:
            self.transform.translate(to_target.normalized * self.speed * dt)


class EnemyRenderer(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(p.x - 10, p.y - 10, 20, 20, engine.Color.RED)


class SceneController(engine.Component):
    """전역 씬 전환을 처리하는 컴포넌트."""

    def on_awake(self):
        self.game_ref = None

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        sm = self.game_ref.scenes

        if kb.is_just_pressed(engine.Key.ESCAPE):
            current = sm.current
            if isinstance(current, PauseScene):
                sm.pop()
            elif isinstance(current, GameScene):
                sm.push(PauseScene())
            elif isinstance(current, GameOverScene):
                sm.replace(TitleScene(self.game_ref))
            elif isinstance(current, TitleScene):
                engine.current_app().quit()

        if kb.is_just_pressed(engine.Key.RETURN):
            current = sm.current
            if isinstance(current, TitleScene):
                sm.replace(GameScene(self.game_ref))
            elif isinstance(current, GameOverScene):
                sm.replace(TitleScene(self.game_ref))


# --- Scenes ---

class TitleScene(engine.Scene):
    def __init__(self, game_ref):
        super().__init__()
        self.game_ref = game_ref

    def on_enter(self):
        controller = engine.Entity("Controller")
        ctrl = controller.add_component(SceneController())
        ctrl.game_ref = self.game_ref
        self.add(controller)

    def draw(self, renderer):
        super().draw(renderer)
        renderer.draw_rect(200, 150, 400, 80, engine.Color.WHITE, filled=False)
        renderer.draw_rect(300, 350, 200, 40, engine.Color.CYAN, filled=False)

    def on_exit(self):
        self.world.clear()


class GameScene(engine.Scene):
    def __init__(self, game_ref):
        super().__init__()
        self.game_ref = game_ref

    def on_enter(self):
        # 컨트롤러
        controller = engine.Entity("Controller")
        ctrl = controller.add_component(SceneController())
        ctrl.game_ref = self.game_ref
        self.add(controller)

        # 플레이어
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_tag("player")
        player.add_component(PlayerMovement())
        player.add_component(PlayerRenderer())
        player.add_component(Health())
        self.add(player)

        # 적 여러 마리
        for i in range(5):
            enemy = engine.Entity(f"Enemy_{i}")
            enemy.position = engine.Vector2(
                random.randint(50, 750),
                random.randint(50, 550),
            )
            enemy.add_tag("enemy")
            enemy.add_component(EnemyAI())
            enemy.add_component(EnemyRenderer())
            hp = enemy.add_component(Health())
            hp.hp = 30
            hp.max_hp = 30
            self.add(enemy)

    def on_pause(self):
        print("게임 일시정지")

    def on_resume(self):
        print("게임 재개")

    def on_exit(self):
        self.world.clear()


class PauseScene(engine.Scene):
    def on_enter(self):
        overlay = engine.Entity("PauseOverlay")
        overlay.add_component(PauseOverlay())
        overlay.add_component(PauseMenu())
        self.add(overlay)

    def draw(self, renderer):
        super().draw(renderer)
        renderer.draw_rect(0, 0, 800, 600, engine.Color(0, 0, 0, 128), layer=50)
        renderer.draw_rect(300, 250, 200, 60, engine.Color.DARK_GRAY, layer=51)
        renderer.draw_rect(300, 250, 200, 60, engine.Color.WHITE, filled=False, layer=51)

    def on_exit(self):
        self.world.clear()


class GameOverScene(engine.Scene):
    def __init__(self, game_ref):
        super().__init__()
        self.game_ref = game_ref

    def on_enter(self):
        controller = engine.Entity("Controller")
        ctrl = controller.add_component(SceneController())
        ctrl.game_ref = self.game_ref
        self.add(controller)

    def draw(self, renderer):
        super().draw(renderer)
        renderer.draw_rect(200, 200, 400, 100, engine.Color(80, 0, 0))
        renderer.draw_rect(200, 200, 400, 100, engine.Color.RED, filled=False)

    def on_exit(self):
        self.world.clear()


# --- Main ---

game = engine.Game(title="Scene Demo", width=800, height=600)
game.run(TitleScene(game))
```

### 흐름 요약

```
프로그램 시작
    |
    v
game.run(TitleScene)
    |
    v
[TitleScene] -- RETURN 키 --> replace(GameScene)
    |
    v
[GameScene] -- ESC 키 --> push(PauseScene)
    |                          |
    |                          v
    |                     [PauseScene] -- ESC 키 --> pop()
    |                          |
    |                          v
    |                     [GameScene] (on_resume)
    |
    |           플레이어 사망 --> replace(GameOverScene)
    |                          |
    |                          v
    |                     [GameOverScene] -- RETURN 키 --> replace(TitleScene)
    |                          |
    v                          v
[TitleScene] -- ESC 키 --> app.quit()
```

---

## SceneManager의 update/draw 흐름

`Game.run()`이 매 프레임 이 흐름을 자동으로 실행한다.

```
scenes.update(dt):
+---------------------------------------------------+
|  if stack is not empty:                           |
|      stack[-1].update(dt)                         |
|          +-- world.update(dt)                     |
|              +-- pending adds                     |
|              +-- on_start (새 컴포넌트)            |
|              +-- on_update(dt) (모든 활성 컴포넌트) |
|              +-- on_late_update(dt)               |
|              +-- pending removes -> on_destroy     |
|                                                   |
|  process_pending()                                |
|      +-- 대기 중인 push/pop/replace/clear 처리    |
|      +-- 해당 씬의 on_enter/on_exit 등 호출       |
+---------------------------------------------------+

scenes.draw(renderer):
+---------------------------------------------------+
|  if stack is not empty:                           |
|      stack[-1].draw(renderer)                     |
|          +-- world.draw(renderer)                 |
|              +-- on_draw(renderer)                |
|                  (모든 활성 컴포넌트)               |
+---------------------------------------------------+
```

> **참고**: `draw()`는 현재(최상위) 씬만 그린다. 일시정지 화면처럼 아래 씬도 보여주고 싶다면, 일시정지 씬에서 아래 씬의 내용을 직접 그리거나, 게임 씬의 마지막 프레임을 캡처해 두는 방식을 사용해야 한다.

---

## 씬 전환이 지연되는 이유

SceneManager의 전환 메서드(push, pop, replace, clear)는 즉시 실행되지 않고 대기열에 추가된다. 이유는 World의 지연 추가/제거와 같다. 씬의 `update()` 실행 중에 씬을 전환하면 예기치 않은 동작이 발생할 수 있기 때문이다.

```python
# Component의 on_update 내에서 씬 전환을 요청해도 안전하다
class BossDefeated(engine.Component):
    def on_update(self, dt):
        hp = self.entity.get_component(Health)
        if hp and not hp.is_alive:
            # 이 시점에 씬 전환을 요청해도 즉시 실행되지 않는다.
            # 현재 프레임의 모든 update가 끝난 후에 처리된다.
            self.game_ref.scenes.replace(VictoryScene())
```

---

## 다음 단계

- [아키텍처 개요](architecture.md) -- 전체 시스템 구조와 데이터 흐름.
- [ECS 시스템](ecs.md) -- Entity, Component, World의 상세 API.
- [시작하기](getting-started.md) -- 처음부터 프로젝트를 설정하는 방법.
