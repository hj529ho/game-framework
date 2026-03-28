# 코어 모듈 (core)

코어 모듈은 엔진의 기반을 구성한다. 생명주기 훅을 정의하는 `Lifecycle`, 게임 루프를 실행하는 `Game`, SDL2 래퍼인 `App`, 프레임 타이밍을 담당하는 `Clock`이 포함되어 있다.

```python
from engine import Lifecycle, Game, App, Clock, current_app
```

---

## Lifecycle 클래스

`Lifecycle`은 게임 오브젝트의 생명주기 훅을 정의하는 베이스 클래스이다. `Component`가 이 클래스를 상속하며, 엔진이 정해진 순서대로 이 훅들을 자동으로 호출한다.

### 훅 호출 순서

```
첫 프레임만:
  on_awake()        -- 컴포넌트가 엔티티에 추가될 때 즉시
  on_start()        -- 첫 on_update 전에 한 번 (모든 형제 컴포넌트가 awake 상태)

매 프레임:
  on_update(dt)       -- 게임 로직, 입력 처리
  on_late_update(dt)  -- 후처리 (카메라 추적, 제약조건)

렌더링:
  on_draw(renderer)   -- 시각적 출력

정리:
  on_destroy()        -- 컴포넌트 또는 엔티티 제거 시
```

### 메서드 (모두 기본적으로 no-op, 서브클래스에서 오버라이드)

| 메서드 | 시그니처 | 호출 시점 |
|---|---|---|
| `on_awake` | `() -> None` | `entity.add_component()` 호출 시 즉시 |
| `on_start` | `() -> None` | 첫 `on_update` 전에 한 번. 모든 형제 컴포넌트가 awake 상태 |
| `on_update` | `(dt: float) -> None` | 매 프레임. `dt` = 초 단위 경과 시간 |
| `on_late_update` | `(dt: float) -> None` | 매 프레임, 모든 on_update 호출 후 |
| `on_draw` | `(renderer: Renderer) -> None` | 매 프레임 렌더링 단계 |
| `on_destroy` | `() -> None` | 컴포넌트 제거 또는 엔티티 파괴 시 |

### on_update vs on_late_update

`on_late_update`는 모든 엔티티의 `on_update`가 완료된 후에 호출된다. 다른 오브젝트의 최종 위치에 의존하는 로직에 적합하다.

```python
class CameraFollow(engine.Component):
    """카메라가 대상을 부드럽게 추적한다."""

    def on_start(self):
        self.target = None
        self.smoothing = 5.0

    def on_late_update(self, dt):
        # 대상의 on_update가 끝난 후 카메라 위치를 갱신한다
        if self.target:
            self.position = self.position.lerp(
                self.target.position, self.smoothing * dt
            )
```

---

## Game 클래스

`Game`은 엔진의 메인 진입점이다. 내부적으로 `App`(SDL2)을 생성하고 게임 루프를 실행한다. 개발자는 `while` 루프를 작성하지 않으며, `Game.run()`이 모든 것을 관리한다.

### 생성자

```python
Game(
    title: str = "Game",        # 윈도우 제목
    width: int = 800,           # 윈도우 너비 (픽셀)
    height: int = 600,          # 윈도우 높이 (픽셀)
    fps: int = 60,              # 목표 FPS
    vsync: bool = True,         # 수직 동기화 활성화
    resizable: bool = False,    # 윈도우 크기 조절 허용
    clear_color: Color = None,  # 배경색 (기본: Color(30, 30, 30))
)
```

### 속성 (Properties)

| 속성 | 타입 | 설명 |
|---|---|---|
| `app` | `App` | 내부 SDL2 앱 (윈도우, 렌더러, 입력, 시계) |
| `scenes` | `SceneManager` | 씬 스택 관리자 |
| `width` | `int` | 윈도우 너비 |
| `height` | `int` | 윈도우 높이 |

### 메서드

| 메서드 | 시그니처 | 설명 |
|---|---|---|
| `run` | `(initial_scene: Scene) -> None` | 게임 루프를 시작한다. `quit()` 호출 또는 윈도우 닫기 전까지 블로킹. |
| `quit` | `() -> None` | 게임 루프를 종료한다. |

### 사용 예제

```python
import engine

class GameScene(engine.Scene):
    def on_enter(self):
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_component(PlayerMovement())
        player.add_component(SpriteRenderer())
        self.add(player)

    def on_exit(self):
        self.world.clear()

game = engine.Game(title="My Game", width=800, height=600)
game.run(GameScene())  # 여기서 블로킹, 게임 종료 시 반환
```

### Game.run() 내부 동작

```
Game.run(initial_scene):
+------------------------------------------+
| 1. scenes.push(initial_scene)            |
| 2. scenes.process_pending()  (on_enter)  |
| 3. while app.running:                    |
|    a. app.poll_events()                  |
|    b. dt = app.clock.tick()              |
|    c. scenes.update(dt)                  |
|    d. app.renderer.begin_frame()         |
|    e. scenes.draw(app.renderer)          |
|    f. app.renderer.end_frame()           |
| 4. finally:                              |
|    a. scenes.clear()                     |
|    b. scenes.process_pending()           |
|    c. app.destroy()                      |
+------------------------------------------+
```

---

## App 클래스

`App`은 SDL2 저수준 래퍼이다. `Game`이 내부적으로 생성하므로, 직접 인스턴스를 만들 필요는 없다. `game.app` 또는 `current_app()`으로 접근한다.

### 생성자

```python
App(
    title: str = "Game",
    width: int = 800,
    height: int = 600,
    fps: int = 60,
    vsync: bool = True,
    resizable: bool = False,
    clear_color: Color = None,
)
```

App 생성 시 자동으로 수행되는 작업:

```
App() 생성자 실행 시:
+------------------------------------------+
| 1. SDL_Init (비디오 + 오디오 초기화)       |
| 2. SDL_CreateWindow (윈도우 생성)          |
| 3. SDL_CreateRenderer (하드웨어 가속 렌더러)|
| 4. Clock 생성 (프레임 타이밍)              |
| 5. Keyboard 생성 (키보드 입력)             |
| 6. Mouse 생성 (마우스 입력)                |
| 7. Renderer 생성 (드로우 큐)               |
| 8. _current_app = self (전역 참조 설정)    |
+------------------------------------------+
```

### 속성 (Properties)

| 속성 | 타입 | 설명 |
|---|---|---|
| `running` | `bool` | `True`이면 게임 루프 유지. `quit()` 또는 윈도우 닫기 시 `False` |
| `clock` | `Clock` | 프레임 타이밍 객체 |
| `keyboard` | `Keyboard` | 키보드 입력 상태 |
| `mouse` | `Mouse` | 마우스 입력 상태 |
| `renderer` | `Renderer` | 드로우 큐 인터페이스 |

### 메서드

#### `poll_events()`

```python
app.poll_events()  # Game.run()이 매 프레임 호출
```

SDL2 이벤트 큐를 폴링하여 처리한다. 내부적으로 다음 순서로 실행된다.

```
poll_events() 내부 동작:
1. keyboard.update()         # previous = current.copy()
2. mouse.update()            # previous = current.copy(), scroll_delta = 0
3. while SDL_PollEvent():
   +-- SDL_QUIT 이벤트  -->  self._running = False
   +-- keyboard.process_event(event)
   +-- mouse.process_event(event)
```

> **참고**: `Game.run()`이 `poll_events()`를 매 프레임 자동으로 호출한다. Component에서 직접 호출할 필요가 없다.

#### `quit()`

```python
app.quit()  # running을 False로 설정
```

`running` 플래그를 `False`로 설정하여 게임 루프를 다음 반복에서 종료시킨다. 현재 프레임의 나머지 코드는 정상적으로 실행된다.

Component에서 게임을 종료하려면:

```python
class QuitOnEscape(engine.Component):
    def on_update(self, dt):
        if engine.current_app().keyboard.is_just_pressed(engine.Key.ESCAPE):
            engine.current_app().quit()
```

#### `destroy()`

```python
app.destroy()  # SDL2 리소스 해제
```

SDL2 렌더러와 윈도우를 파괴하고, `SDL_Quit()`을 호출하여 모든 SDL2 서브시스템을 종료한다. `Game.run()` 내부의 `finally` 블록에서 자동으로 호출되므로, 직접 호출할 필요가 없다.

---

## Clock 클래스

`Clock`은 고해상도 프레임 타이밍을 제공한다. SDL2의 `SDL_GetPerformanceCounter`를 사용하여 마이크로초 수준의 정밀도로 시간을 측정한다.

### 생성자

```python
Clock(target_fps: int = 60)
```

`Game`이 내부적으로 생성하므로, 직접 생성할 필요는 거의 없다. `current_app().clock`으로 접근한다.

### `tick()` 메서드

```python
dt = app.clock.tick()  # 반환: 초 단위의 델타 타임 (float)
```

`tick()`은 다음 작업을 수행한다.

```
tick() 내부 동작:
1. 현재 시간 측정 (SDL_GetPerformanceCounter)
2. 이전 tick()과의 시간차 계산 -> dt
3. dt < 목표 프레임 시간(1/fps)이면:
   +-- 차이만큼 SDL_Delay로 대기
   +-- 대기 후 다시 시간 측정하여 dt 갱신
4. total_time += dt
5. frame_count += 1
6. FPS 통계 갱신 (0.5초마다)
7. return dt
```

### 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `dt` | `float` | 마지막 프레임의 델타 타임 (초). `tick()`의 반환값과 동일 |
| `fps` | `float` | 스무딩된 FPS (0.5초마다 갱신) |
| `total_time` | `float` | 첫 `tick()`부터의 총 경과 시간 (초) |
| `frame_count` | `int` | 총 프레임 수 |
| `target_fps` | `int` | 목표 FPS (읽기/쓰기 가능) |

### 델타 타임이란?

델타 타임(dt)은 **이전 프레임과 현재 프레임 사이의 경과 시간**이다. 60 FPS에서 이상적인 dt는 약 `0.01667`초(1/60)이다.

```
프레임 1          프레임 2          프레임 3
   |--- 16.7ms ----|--- 16.7ms ----|
   |   dt = 0.0167 |  dt = 0.0167  |
```

델타 타임을 사용하면 프레임 속도가 변해도 게임 동작이 일관되게 유지된다.

```python
# 잘못된 방법: FPS에 따라 이동 속도가 달라짐
self.position.x += 5  # 60fps = 300px/s, 30fps = 150px/s

# 올바른 방법: FPS와 무관하게 초당 300픽셀 이동
speed = 300.0
self.transform.translate(engine.Vector2(speed * dt, 0))  # 항상 300px/s
```

### FPS 제한 동작

Clock은 목표 FPS를 초과하지 않도록 프레임 시간을 제한한다.

```
목표 FPS: 60  =>  목표 프레임 시간: 16.67ms

프레임 처리 시간이 10ms인 경우:
[==처리==][...대기 6.67ms...]
|<---------- 16.67ms ---------->|

프레임 처리 시간이 20ms인 경우 (목표 초과):
[=========처리=========]
|<------- 20ms ------->|  <- 대기 없이 즉시 다음 프레임
```

vsync가 활성화된 경우, 모니터 주사율에 의해 추가적인 프레임 동기화가 이루어진다.

### target_fps 동적 변경

Component에서 FPS를 동적으로 변경할 수 있다.

```python
class PerformanceSettings(engine.Component):
    def on_update(self, dt):
        kb = engine.current_app().keyboard
        if kb.is_just_pressed(engine.Key.F1):
            engine.current_app().clock.target_fps = 30
        if kb.is_just_pressed(engine.Key.F2):
            engine.current_app().clock.target_fps = 60
        if kb.is_just_pressed(engine.Key.F3):
            engine.current_app().clock.target_fps = 120
```

---

## current_app() 함수

```python
from engine import current_app

app = current_app()  # 현재 활성 App 인스턴스 반환
```

`current_app()`은 어디서든 현재 실행 중인 `App` 인스턴스에 접근할 수 있게 해주는 전역 함수이다.

### 동작 원리

`App`의 생성자가 실행되면 모듈 수준의 `_current_app` 변수에 자기 자신을 저장한다. `current_app()`은 이 변수를 반환한다.

```python
# engine/core/app.py 내부
_current_app: App | None = None

def current_app() -> App:
    if _current_app is None:
        raise RuntimeError("No App instance is running.")
    return _current_app

class App:
    def __init__(self, ...):
        global _current_app
        # ... 초기화 ...
        _current_app = self
```

### 사용 시점

`current_app()`은 주로 **Component** 내부에서 입력 상태나 시계에 접근할 때 사용한다. Component의 `on_update`나 `on_draw` 메서드는 `app` 인스턴스를 직접 받지 않으므로, 전역 함수를 통해 접근한다.

```python
class PlayerMovement(engine.Component):
    def on_start(self):
        self.speed = 200.0

    def on_update(self, dt):
        app = engine.current_app()
        kb = app.keyboard

        direction = engine.Vector2.zero()
        if kb.is_pressed(engine.Key.W):
            direction = direction + engine.Vector2.up()
        if kb.is_pressed(engine.Key.S):
            direction = direction + engine.Vector2.down()
        if kb.is_pressed(engine.Key.A):
            direction = direction + engine.Vector2.left()
        if kb.is_pressed(engine.Key.D):
            direction = direction + engine.Vector2.right()

        if direction.magnitude > 0:
            self.transform.translate(direction.normalized * self.speed * dt)


class SpriteRenderer(engine.Component):
    def on_awake(self):
        self.color = engine.Color.CYAN
        self.size = 32

    def on_draw(self, renderer):
        p = self.position
        half = self.size / 2
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size, self.color)
```

### 주의 사항

- `App` 인스턴스가 생성되기 전에 `current_app()`을 호출하면 `RuntimeError`가 발생한다.
- `app.destroy()` 이후에는 `_current_app`이 `None`이 되므로, 역시 `RuntimeError`가 발생한다.
- 한 프로세스에서 `App` 인스턴스는 하나만 존재한다고 가정한다.

---

## 다음 단계

- [수학 모듈](math.md) -- 벡터, 사각형, 원, 변환을 다루는 수학 도구.
- [입력 시스템](input.md) -- 키보드와 마우스 입력 상태 관리.
- [렌더링](rendering.md) -- 지연 드로우 큐와 레이어 기반 렌더링.
