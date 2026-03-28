# 시작하기

## 엔진 소개

이 엔진은 **SDL2(PySDL2) 기반의 Python 2D 게임 엔진**이다. SDL2는 크로스 플랫폼 멀티미디어 라이브러리로, 윈도우 생성, 2D 렌더링, 키보드/마우스 입력 등 게임 개발에 필요한 저수준 기능을 제공한다. 이 엔진은 SDL2의 Python 바인딩인 PySDL2를 사용하여, Python 개발자가 복잡한 C 코드 없이도 빠르고 효율적인 2D 게임을 만들 수 있도록 설계되었다.

### 핵심 특징

- **엔진 관리 생명주기**: `Game.run()`이 게임 루프를 내부적으로 실행한다. 개발자는 `while` 루프를 작성하지 않고, `Component`의 생명주기 훅을 통해 동작을 정의한다.
- **유니티 스타일 컴포넌트 패턴**: `Lifecycle` 베이스 클래스를 `Component`가 상속하고, `Entity`에 부착한다. Entity는 순수 컨테이너(유니티의 GameObject)이며 자체 동작이 없다. 모든 게임 로직은 Component에서 구현한다.
- **지연 렌더링(Deferred Draw Queue)**: 그리기 명령을 즉시 실행하지 않고 큐에 모은 뒤, 레이어 순서대로 정렬하여 한 번에 렌더링한다.
- **스택 기반 씬 관리**: 게임 화면, 일시정지 메뉴, 타이틀 화면 등을 씬 스택으로 관리한다.

---

## 설치 방법

### 사전 요구 사항

- Python 3.10 이상
- pip (Python 패키지 관리자)

### 1단계: SDL2 런타임 라이브러리 설치

PySDL2는 SDL2 라이브러리의 Python 바인딩이므로, SDL2 런타임 DLL이 시스템에 설치되어 있어야 한다. 가장 간단한 방법은 `pysdl2-dll` 패키지를 함께 설치하는 것이다.

```bash
pip install pysdl2 pysdl2-dll
```

> **참고**: `pysdl2-dll`은 Windows, macOS, Linux에서 SDL2 바이너리를 자동으로 제공한다. 수동으로 SDL2를 설치한 경우에는 `pysdl2-dll` 없이 `pysdl2`만 설치해도 된다.

### 2단계: 엔진 설치

프로젝트 디렉토리에서 엔진을 설치한다.

```bash
# 프로젝트 루트 디렉토리에서
pip install -e .
```

또는 `src` 디렉토리를 Python 경로에 추가한다.

```bash
# 환경 변수 설정 (개발 중)
export PYTHONPATH=/path/to/game-framework/src:$PYTHONPATH
```

### 의존성 요약

| 패키지 | 용도 |
|---|---|
| `pysdl2` | SDL2의 Python 바인딩 (윈도우, 렌더링, 입력) |
| `pysdl2-dll` | SDL2 런타임 라이브러리 자동 배포 (선택사항) |

---

## 최소 예제

다음은 윈도우를 열고 파란색 사각형을 키보드로 움직이는 가장 간단한 예제이다. 이 엔진에서 모든 게임 로직은 Component에서 작성하며, `Game.run()`이 루프를 관리한다.

```python
import engine

# --- Component 정의 ---

class Movement(engine.Component):
    """키보드 이동을 처리하는 컴포넌트."""

    def on_start(self):
        self.speed = 300.0

    def on_update(self, dt):
        app = engine.current_app()
        kb = app.keyboard
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


class BoxRenderer(engine.Component):
    """사각형을 그리는 컴포넌트."""

    def on_awake(self):
        self.color = engine.Color.BLUE
        self.size = 64

    def on_draw(self, renderer):
        p = self.position
        half = self.size / 2
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size, self.color)


class QuitOnEscape(engine.Component):
    """ESC 키로 게임을 종료하는 컴포넌트."""

    def on_update(self, dt):
        if engine.current_app().keyboard.is_just_pressed(engine.Key.ESCAPE):
            engine.current_app().quit()


# --- Scene 정의 ---

class GameScene(engine.Scene):
    def on_enter(self):
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_component(Movement())
        player.add_component(BoxRenderer())
        player.add_component(QuitOnEscape())
        self.add(player)


# --- 실행 ---

game = engine.Game(title="Hello World", width=800, height=600)
game.run(GameScene())
```

이 코드를 실행하면 800x600 크기의 윈도우가 열리고, 어두운 배경 위에 파란색 사각형이 표시된다. 방향키로 사각형을 움직일 수 있으며, ESC 키 또는 윈도우의 닫기(X) 버튼을 누르면 프로그램이 종료된다.

---

## 엔진 관리 게임 루프

이 엔진의 핵심 설계 원칙은 **엔진이 게임 루프를 관리한다**는 것이다. 개발자가 `while` 루프를 직접 작성하지 않으며, `Game.run()`이 내부적으로 모든 프레임 처리를 수행한다. 개발자는 Component의 생명주기 훅(on_update, on_draw 등)을 오버라이드하여 동작을 정의한다.

### 게임 루프의 구조

```
+-------------------------------------------------------------+
|                    Game.run() 내부 루프                       |
|                                                              |
|   poll_events()  ->  clock.tick()  ->  Scene.update(dt)      |
|        |                  |                    |             |
|   이벤트 처리        델타 타임 계산     World 업데이트          |
|   (입력 갱신)       (FPS 제한)        (on_start, on_update,  |
|                                        on_late_update)       |
|                                                              |
|   begin_frame()  ->  Scene.draw(renderer)  ->  end_frame()   |
|        |                    |                       |        |
|   화면 초기화         Component.on_draw          큐 실행 및   |
|   (큐 초기화)        (큐에 추가)                  화면 표시    |
+-------------------------------------------------------------+
```

### 프레임당 생명주기 순서

```
Game.run() loop:
  1. App.poll_events()               -- SDL 이벤트 폴링, 입력 상태 갱신
  2. Clock.tick()                    -- 델타 타임 계산
  3. Scene.update(dt):
     a. World._process_additions()   -- 대기 중인 엔티티 추가
     b. Component.on_start()         -- 새 컴포넌트만 (첫 프레임)
     c. Component.on_update(dt)      -- 매 프레임
     d. Component.on_late_update(dt) -- 모든 on_update 이후
     e. World._process_removals()    -- 대기 중인 엔티티 제거 + on_destroy
  4. Renderer.begin_frame()          -- 화면 지우기
  5. Scene.draw(renderer):
     a. Component.on_draw(renderer)  -- 모든 활성 컴포넌트
  6. Renderer.end_frame()            -- 레이어 정렬, 실행, 화면 표시
  7. SceneManager.process_pending()  -- 씬 전환 처리
```

### 각 단계의 역할

1. **`App.poll_events()`** -- SDL2 이벤트를 폴링한다. 키보드와 마우스 상태가 갱신되며, 윈도우 닫기 이벤트가 발생하면 `app.running`이 `False`가 된다.

2. **`Clock.tick()`** -- 프레임 간 경과 시간(델타 타임)을 계산하고, 목표 FPS를 초과하지 않도록 필요시 대기(sleep)한다.

3. **`Scene.update(dt)`** -- World가 엔티티의 추가/제거를 처리하고, 모든 활성 컴포넌트의 on_start, on_update, on_late_update를 호출한다.

4. **`Renderer.begin_frame()`** -- 드로우 큐를 초기화하고, `clear_color`로 화면을 지운다.

5. **`Scene.draw(renderer)`** -- 모든 활성 컴포넌트의 on_draw를 호출한다. 그리기 명령은 내부 큐에 저장된다.

6. **`Renderer.end_frame()`** -- 큐에 저장된 그리기 명령을 레이어 순서대로 정렬 후 실행하고, `SDL_RenderPresent`로 화면에 표시한다.

---

## 움직이는 사각형 예제

키보드 입력으로 사각형을 움직이는 예제를 살펴보자. 모든 로직은 Component에서 작성한다.

```python
import engine

class PlayerMovement(engine.Component):
    """8방향 이동을 처리하는 컴포넌트."""

    def on_start(self):
        self.speed = 200.0  # 초당 200픽셀

    def on_update(self, dt):
        kb = engine.current_app().keyboard

        # 방향키 입력으로 이동 방향 계산
        direction = engine.Vector2.zero()
        if kb.is_pressed(engine.Key.UP):
            direction = direction + engine.Vector2.up()
        if kb.is_pressed(engine.Key.DOWN):
            direction = direction + engine.Vector2.down()
        if kb.is_pressed(engine.Key.LEFT):
            direction = direction + engine.Vector2.left()
        if kb.is_pressed(engine.Key.RIGHT):
            direction = direction + engine.Vector2.right()

        # 대각선 이동 시 속도 정규화
        if direction.magnitude > 0:
            direction = direction.normalized

        # 위치 갱신 (속도 * 방향 * 델타 타임)
        self.transform.translate(direction * self.speed * dt)


class BoxRenderer(engine.Component):
    """초록색 사각형을 그리는 컴포넌트."""

    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(p.x - 16, p.y - 16, 32, 32, engine.Color.GREEN)


class GameScene(engine.Scene):
    def on_enter(self):
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_component(PlayerMovement())
        player.add_component(BoxRenderer())
        self.add(player)


game = engine.Game(title="Moving Box", width=800, height=600)
game.run(GameScene())
```

이 예제에서 주목할 점:

- **`is_pressed`**를 사용하면 키를 누르고 있는 동안 계속 이동한다.
- **델타 타임(`dt`)**을 곱하여 프레임 속도와 무관하게 초당 200픽셀로 이동한다.
- **정규화(normalized)**로 대각선 이동 시 속도가 빨라지는 문제를 방지한다.
- **`self.transform.translate()`**로 현재 위치에 오프셋을 더한다.

---

## 예제 실행 방법

### 명령줄에서 실행

```bash
# 프로젝트 루트 디렉토리에서
python examples/minimal.py
```

### PYTHONPATH가 설정되지 않은 경우

```bash
# src 디렉토리를 경로에 포함하여 실행
PYTHONPATH=src python examples/minimal.py
```

### Windows에서 실행

```powershell
# PowerShell
$env:PYTHONPATH = "src"
python examples\minimal.py
```

### 문제 해결

| 증상 | 원인 | 해결 방법 |
|---|---|---|
| `ModuleNotFoundError: No module named 'sdl2'` | PySDL2가 설치되지 않음 | `pip install pysdl2 pysdl2-dll` |
| `RuntimeError: SDL2 init failed` | SDL2 DLL을 찾을 수 없음 | `pip install pysdl2-dll` 또는 SDL2를 수동 설치 |
| `ModuleNotFoundError: No module named 'engine'` | 엔진이 Python 경로에 없음 | `pip install -e .` 또는 `PYTHONPATH=src` 설정 |
| 윈도우가 바로 닫힘 | 스크립트에 오류가 있음 | 터미널에서 실행하여 오류 메시지 확인 |

---

## 다음 단계

- [아키텍처 개요](architecture.md) -- 엔진의 전체 구조와 설계 철학을 이해한다.
- [코어 모듈](core.md) -- `Game`, `App`, `Clock`의 상세 사용법을 배운다.
- [ECS 시스템](ecs.md) -- Entity, Component, World를 사용하여 게임 오브젝트를 관리한다.
- [씬 관리](scene.md) -- 여러 화면(씬)을 전환하는 방법을 배운다.
