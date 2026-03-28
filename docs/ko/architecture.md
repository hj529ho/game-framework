# 아키텍처 개요

## 전체 아키텍처 다이어그램

이 엔진은 7개의 핵심 모듈로 구성되어 있으며, 각 모듈은 명확한 책임을 가진다.

```
+================================================================+
|                         engine (최상위)                          |
|   모든 공개 심볼을 re-export. import engine 으로 전부 사용 가능   |
+================================================================+
        |           |          |           |           |
        v           v          v           v           v
  +---------+ +---------+ +---------+ +---------+ +---------+
  |  core   | |  math   | |  input  | |renderer | |  scene  |
  |         | |         | |         | |         | |         |
  |Lifecycle| | Vector2 | | Keyboard| | Renderer| | Scene   |
  | Game    | | Rect    | | Mouse   | | Color   | | Scene   |
  | App     | | Circle  | | Key     | |         | | Manager |
  | Clock   | |Transform| | Mouse   | |         | |         |
  | current | | 2D      | | Button  | |         | |         |
  | _app()  | | utils   | |         | |         | |         |
  +---------+ +---------+ +---------+ +---------+ +---------+
                                                       |
                                                       v
                                                 +---------+
                                                 |   ecs   |
                                                 |         |
                                                 | Entity  |
                                                 |Component|
                                                 | World   |
                                                 +---------+
```

---

## 모듈 의존성 그래프

아래 다이어그램은 모듈 간 의존 관계를 나타낸다. 화살표는 "의존한다" 방향이다.

```
                    engine (최상위 패키지)
                    /    |    |     \     \
                   v     v    v      v     v
                core   math  input  renderer  scene
                 |      |     |       |        |
                 |      |     |       |        +---> ecs
                 |      |     |       |              / \
                 |      |     |       |             v   v
                 |      |     |       |         entity  component
                 |      |     |       |           |        |
                 |      |     |       |           |        +---> core.lifecycle
                 |      |     |       |           +---> math (Vector2, Transform2D)
                 v      |     v       v
            Game,Clock  |  Keyboard  Renderer
                        |  Mouse       |
                        |     |        +---> math (Vector2)
                        |     +-----------> math (Vector2)
                        |     +-----------> keys (Key, MouseButton)
                        v
                  Vector2, Rect, Circle, Transform2D, utils
```

### 의존 방향 원칙

- **math** 모듈은 다른 엔진 모듈에 의존하지 않는다 (순수 수학 연산).
- **core.lifecycle**은 다른 모듈에 의존하지 않는다 (생명주기 훅 인터페이스 정의).
- **input** 모듈은 math(Vector2)와 SDL2에만 의존한다.
- **renderer** 모듈은 math(Vector2)와 SDL2에 의존한다.
- **ecs** 모듈은 math(Vector2, Transform2D)와 core.lifecycle에 의존한다.
- **scene** 모듈은 ecs(Entity, World)에 의존한다.
- **core.Game**은 App, SceneManager를 생성하고 게임 루프를 실행한다.

---

## 설계 철학

### 1. 엔진 관리 생명주기

이 엔진은 `Game.run()`이 게임 루프를 소유하고, 개발자는 Component의 생명주기 훅을 통해 동작을 정의하는 방식이다. 유니티의 MonoBehaviour 패턴과 유사하다.

```
+---------------------------------------------------+
|              엔진 관리 방식 (이 엔진)                |
|                                                    |
|  game = Game(title="My Game", width=800, height=600)
|  game.run(MyScene())                               |
|                                                    |
|  엔진이 루프를 제어한다.                             |
|  개발자는 Component 훅을 오버라이드한다:              |
|    on_awake, on_start, on_update,                  |
|    on_late_update, on_draw, on_destroy             |
+---------------------------------------------------+
```

이 방식의 장점:
- 프레임 타이밍, 생명주기 순서를 엔진이 보장한다.
- Component의 생명주기 훅만 신경 쓰면 되므로 구조가 명확하다.
- 씬 전환, 엔티티 추가/제거의 타이밍을 엔진이 안전하게 관리한다.

### 2. 유니티 스타일 컴포넌트 패턴

이 엔진의 핵심 패턴은 유니티의 GameObject + MonoBehaviour 구조를 따른다.

```
+--------------------------------------------------+
|  Lifecycle (base)                                 |
|    on_awake, on_start, on_update,                |
|    on_late_update, on_draw, on_destroy           |
|                                                   |
|       |                                           |
|       v                                           |
|  Component (Lifecycle 상속)                       |
|    + entity, transform, position, enabled         |
|    + 모든 게임 로직은 여기에서                      |
|                                                   |
|       |                                           |
|       v                                           |
|  Entity (순수 컨테이너, 유니티의 GameObject)        |
|    + Transform2D + Components + Tags + Children   |
|    + 자체 동작 없음 (on_update/on_draw 없음)       |
+--------------------------------------------------+
```

- **Entity**는 순수 컨테이너이다. Transform, 컴포넌트 목록, 태그, 자식 엔티티만 가진다.
- **Component**가 모든 동작을 담당한다. 이동, 렌더링, AI, 입력 처리 등 모든 로직은 Component에서 구현한다.
- 하나의 Entity에 여러 Component를 부착하여 동작을 조합한다.

### 3. SDL2 백엔드

엔진은 내부적으로 모든 저수준 작업에 SDL2를 사용한다.

| 기능 | SDL2 함수 |
|---|---|
| 윈도우 생성 | `SDL_CreateWindow` |
| 렌더러 생성 | `SDL_CreateRenderer` |
| 이벤트 폴링 | `SDL_PollEvent` |
| 키보드 입력 | `SDL_KEYDOWN`, `SDL_KEYUP` 이벤트 |
| 마우스 입력 | `SDL_MOUSEMOTION`, `SDL_MOUSEBUTTONDOWN` 등 |
| 사각형 렌더링 | `SDL_RenderFillRect`, `SDL_RenderDrawRect` |
| 선 렌더링 | `SDL_RenderDrawLine` |
| 텍스처 렌더링 | `SDL_RenderCopy`, `SDL_RenderCopyEx` |
| 프레임 표시 | `SDL_RenderPresent` |
| 타이밍 | `SDL_GetPerformanceCounter`, `SDL_Delay` |

PySDL2는 SDL2의 C 함수를 Python에서 직접 호출할 수 있게 해주는 ctypes 기반 바인딩이다. 이 엔진은 PySDL2 위에 Python답게 사용하기 쉬운 래퍼를 제공한다.

### 4. 지연 렌더링 (Deferred Draw Queue)

그리기 함수를 호출해도 화면에 즉시 그려지지 않는다. 대신 **드로우 큐(draw queue)**에 명령이 추가된다.

```
프레임 시작                          프레임 끝
    |                                    |
    v                                    v
begin_frame()                       end_frame()
    |                                    |
    +-- 큐 초기화                         +-- 큐를 레이어 순서로 정렬
    +-- 화면 클리어                       +-- 모든 명령 순차 실행
                                         +-- SDL_RenderPresent
    draw_rect(... layer=0)
    draw_line(... layer=1)     --->  실행 순서:
    draw_rect(... layer=-1)           1. layer=-1: draw_rect (배경)
    draw_texture(... layer=0)         2. layer= 0: draw_rect (호출 순서 1번째)
                                      3. layer= 0: draw_texture (호출 순서 2번째)
                                      4. layer= 1: draw_line (전경)
```

이 방식의 장점:
- **레이어 시스템**: 그리기 호출 순서와 무관하게, 레이어 값으로 앞뒤 관계를 결정한다.
- **안정 정렬(Stable Sort)**: 같은 레이어 내에서는 호출 순서가 유지된다.
- **배치 최적화 가능**: 미래에 같은 텍스처를 묶어서 한 번에 그리는 최적화가 가능하다.

### 5. 스택 기반 씬 관리

SceneManager는 씬을 **스택(Stack)** 자료구조로 관리한다.

```
push(GameScene)     push(PauseMenu)     pop()            replace(GameOver)

+-----------+       +-----------+       +-----------+    +-----------+
|           |       |PauseMenu  |       |           |    | GameOver  |
+-----------+       +-----------+       +-----------+    +-----------+
| GameScene |       | GameScene |       | GameScene |
+-----------+       +-----------+       +-----------+
```

- **push**: 새 씬을 스택 위에 올린다. 아래 씬은 일시정지(on_pause).
- **pop**: 최상위 씬을 제거한다. 아래 씬이 재개(on_resume).
- **replace**: 최상위 씬을 새 씬으로 교체한다.
- **clear**: 모든 씬을 제거한다.

---

## 데이터 흐름

매 프레임마다 데이터는 다음 경로를 따라 흐른다. `Game.run()`이 이 전체 흐름을 관리한다.

```
  SDL2 이벤트        입력 상태          컴포넌트 로직       드로우 큐        화면 출력
 ============    =============    ==============    =============    ===========

  SDL_PollEvent   keyboard         Component        draw_rect()     SDL_Render
  ------------->  .is_pressed()    .on_update(dt)   draw_line()     Present
                  .is_just_       ===============>  draw_texture()  ===========>
  SDL_KEYDOWN     pressed()        Component        =============>
  SDL_KEYUP      ===============>  .on_late_update  Renderer
  SDL_MOUSE*      mouse            (dt)             .end_frame()
                  .position                          - 정렬
                  .is_pressed()    Component          - 실행
                                   .on_draw           - 표시
                                   (renderer)
```

### 프레임 상세 흐름

```
Game.run() 내부:
1. app.poll_events()
   +-- keyboard.update()          # 이전 프레임 상태를 previous로 복사
   +-- mouse.update()             # 이전 프레임 상태를 previous로 복사, scroll 초기화
   +-- SDL_PollEvent 루프:
       +-- SDL_QUIT -> app.running = False
       +-- keyboard.process_event(event)  # current 상태 갱신
       +-- mouse.process_event(event)     # current 상태 갱신

2. dt = app.clock.tick()
   +-- 델타 타임 계산 (SDL_GetPerformanceCounter)
   +-- FPS 제한 (SDL_Delay)
   +-- FPS 통계 갱신 (0.5초마다)

3. scenes.update(dt)
   +-- scene.world.update(dt):
       +-- 대기 중인 엔티티 추가
       +-- 새 컴포넌트의 on_start() 호출
       +-- 모든 활성 컴포넌트의 on_update(dt) 호출
       +-- 모든 활성 컴포넌트의 on_late_update(dt) 호출
       +-- 대기 중인 엔티티 제거 (on_destroy 호출)
   +-- scene_manager.process_pending()  # 씬 전환 처리

4. app.renderer.begin_frame()
   +-- 드로우 큐 초기화
   +-- clear_color로 화면 클리어

5. scenes.draw(app.renderer)
   +-- 모든 활성 컴포넌트의 on_draw(renderer) 호출
   +-- 각 컴포넌트가 renderer.draw_rect() 등을 호출
   +-- 명령들이 드로우 큐에 축적

6. app.renderer.end_frame()
   +-- 드로우 큐를 (layer, order) 기준으로 정렬
   +-- 정렬된 순서대로 SDL2 렌더링 함수 실행
   +-- SDL_RenderPresent로 화면 표시
```

---

## 모듈별 요약

| 모듈 | 파일 경로 | 핵심 클래스 | 책임 |
|---|---|---|---|
| `core` | `src/engine/core/` | `Lifecycle`, `Game`, `App`, `Clock` | 생명주기 정의, 게임 루프, SDL2 초기화, 타이밍 |
| `math` | `src/engine/math/` | `Vector2`, `Rect`, `Circle`, `Transform2D` | 수학 연산, 충돌 프리미티브 |
| `input` | `src/engine/input/` | `Keyboard`, `Mouse`, `Key`, `MouseButton` | 키보드/마우스 입력 |
| `renderer` | `src/engine/renderer/` | `Renderer`, `Color` | 지연 드로우 큐, 렌더링 |
| `ecs` | `src/engine/ecs/` | `Entity`, `Component`, `World` | 게임 오브젝트 관리 |
| `scene` | `src/engine/scene/` | `Scene`, `SceneManager` | 씬 스택 관리 |

---

## 다음 단계

- [코어 모듈](core.md) -- Game, App, Clock의 상세 API를 알아본다.
- [수학 모듈](math.md) -- 벡터, 충돌, 보간 함수를 배운다.
- [입력 시스템](input.md) -- 키보드와 마우스 처리 방법을 배운다.
- [렌더링](rendering.md) -- 지연 드로우 큐와 레이어 시스템을 이해한다.
