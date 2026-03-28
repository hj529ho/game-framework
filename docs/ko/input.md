# 입력 시스템 (input)

입력 모듈은 키보드와 마우스 상태를 관리한다. **더블 버퍼링** 방식을 사용하여 현재 프레임과 이전 프레임의 상태를 비교함으로써 "눌림", "방금 눌림", "방금 떼어짐" 세 가지 상태를 정확하게 구분한다.

```python
from engine import Key, MouseButton, Keyboard, Mouse
```

> **참고**: `Game.run()`이 매 프레임 시작에 `poll_events()`를 자동으로 호출하므로, Component에서는 별도의 이벤트 폴링 없이 바로 입력 상태를 조회할 수 있다. `current_app().keyboard` 또는 `current_app().mouse`로 접근한다.

---

## 더블 버퍼 방식

입력 시스템의 핵심은 **두 개의 버퍼(current, previous)**를 유지하는 것이다.

```
프레임 N-1             프레임 N              프레임 N+1

  [current]     ---->  [previous]
  (키 상태)       복사   (이전 프레임 상태)

                       [current]
                       (새 이벤트 반영)
```

`poll_events()` 호출 시 내부 동작:

```
1. keyboard.update()
   +-- previous = current.copy()    # 현재 상태를 이전으로 복사

2. mouse.update()
   +-- previous = current.copy()    # 현재 상태를 이전으로 복사
   +-- scroll_delta = 0.0           # 스크롤 초기화

3. SDL 이벤트 루프:
   +-- KEYDOWN  -> current에 키 추가
   +-- KEYUP    -> current에서 키 제거
   +-- MOUSEMOTION -> position 갱신
   +-- MOUSEBUTTONDOWN -> current에 버튼 추가
   +-- MOUSEBUTTONUP -> current에서 버튼 제거
   +-- MOUSEWHEEL -> scroll_delta 누적
```

이 방식 덕분에 아래 세 가지 상태를 정확하게 판단할 수 있다.

| 상태 | previous | current | 의미 |
|---|---|---|---|
| **is_pressed** | (무관) | 있음 | 키/버튼이 눌려 있음 (계속 누르는 중 포함) |
| **is_just_pressed** | 없음 | 있음 | 이번 프레임에 처음 눌림 |
| **is_just_released** | 있음 | 없음 | 이번 프레임에 떼어짐 |

---

## Keyboard

### is_pressed vs is_just_pressed vs is_just_released

세 메서드의 차이를 프레임별 타이밍 다이어그램으로 살펴보자.

```
사용자가 스페이스바를 누르고 있는 상황:

프레임:    1     2     3     4     5     6     7     8
키 상태:  [ ]   [V]   [V]   [V]   [V]   [ ]   [ ]   [ ]
          안눌림 눌림  눌림  눌림  눌림  떼어짐 안눌림 안눌림

is_pressed:
          false TRUE  TRUE  TRUE  TRUE  false false false
                ^^^^  ^^^^  ^^^^  ^^^^
                누르고 있는 동안 계속 True

is_just_pressed:
          false TRUE  false false false false false false
                ^^^^
                처음 누른 프레임에만 True

is_just_released:
          false false false false false TRUE  false false
                                       ^^^^
                                       떼는 프레임에만 True
```

### 사용법

Component 내에서 `current_app().keyboard`로 키보드 상태에 접근한다.

```python
import engine

class PlayerInput(engine.Component):
    def on_update(self, dt):
        kb = engine.current_app().keyboard

        # 키를 누르고 있는 동안 계속 실행 (이동 등)
        if kb.is_pressed(engine.Key.RIGHT):
            self.transform.translate(engine.Vector2.right() * self.speed * dt)

        # 키를 처음 누른 순간에만 실행 (점프, 사격 등)
        if kb.is_just_pressed(engine.Key.SPACE):
            self.jump()

        # 키를 떼는 순간에만 실행 (차징 공격 발사 등)
        if kb.is_just_released(engine.Key.SPACE):
            self.release_charged_attack()
```

### Key enum

`Key`는 SDL2의 `SDLK_*` 상수를 래핑한 `IntEnum`이다.

| 그룹 | 멤버 |
|---|---|
| 알파벳 | `Key.A` ~ `Key.Z` |
| 숫자 | `Key.NUM_0` ~ `Key.NUM_9` |
| 방향키 | `Key.UP`, `Key.DOWN`, `Key.LEFT`, `Key.RIGHT` |
| 특수키 | `Key.SPACE`, `Key.RETURN`, `Key.ESCAPE`, `Key.TAB`, `Key.BACKSPACE`, `Key.DELETE` |
| 수정자 | `Key.LSHIFT`, `Key.RSHIFT`, `Key.LCTRL`, `Key.RCTRL`, `Key.LALT`, `Key.RALT` |
| 기능키 | `Key.F1` ~ `Key.F12` |

---

## Mouse

### 위치

마우스 위치는 화면 좌표(픽셀)로 제공된다.

```python
import engine

class MouseTracker(engine.Component):
    def on_update(self, dt):
        mouse = engine.current_app().mouse

        # 현재 마우스 위치
        pos = mouse.position
        print(f"마우스 위치: ({pos.x}, {pos.y})")
```

```
(0, 0) -------> x+
  |  +---------------------+
  |  |                     |
  |  |       * (pos.x,     |
  v  |         pos.y)      |
  y+ |                     |
     +---------------------+
                      (width, height)
```

### 버튼 상태

키보드와 동일한 3가지 상태 메서드를 제공한다.

```python
class DrawTool(engine.Component):
    def on_update(self, dt):
        mouse = engine.current_app().mouse

        # 왼쪽 버튼을 누르고 있는 동안
        if mouse.is_pressed(engine.MouseButton.LEFT):
            self.draw_at(mouse.position)

        # 왼쪽 버튼을 처음 클릭한 순간
        if mouse.is_just_pressed(engine.MouseButton.LEFT):
            self.start_drag(mouse.position)

        # 왼쪽 버튼을 떼는 순간
        if mouse.is_just_released(engine.MouseButton.LEFT):
            self.end_drag(mouse.position)
```

### MouseButton enum

| 멤버 | 설명 |
|---|---|
| `MouseButton.LEFT` | 왼쪽 마우스 버튼 |
| `MouseButton.MIDDLE` | 가운데 마우스 버튼 (휠 클릭) |
| `MouseButton.RIGHT` | 오른쪽 마우스 버튼 |

### 스크롤

마우스 휠 스크롤량을 `scroll_delta` 속성으로 읽을 수 있다. 위로 스크롤하면 양수, 아래로 스크롤하면 음수이다. 매 프레임 초기화된다.

```python
class ZoomController(engine.Component):
    def on_update(self, dt):
        scroll = engine.current_app().mouse.scroll_delta
        if scroll > 0:
            self.zoom_in()
        elif scroll < 0:
            self.zoom_out()
```

```
scroll_delta 값:

  위로 스크롤:   +1, +2, ...  (양수)
  스크롤 안 함:   0
  아래로 스크롤: -1, -2, ...  (음수)
```

---

## 일반적인 패턴

### 1. 8방향 이동

WASD 또는 방향키로 8방향 이동하는 가장 일반적인 패턴이다.

```python
import engine

class PlayerMovement(engine.Component):
    def on_start(self):
        self.speed = 200.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard

        # 입력에 따라 방향 벡터 구성
        direction = engine.Vector2.zero()

        if kb.is_pressed(engine.Key.W) or kb.is_pressed(engine.Key.UP):
            direction = direction + engine.Vector2.up()
        if kb.is_pressed(engine.Key.S) or kb.is_pressed(engine.Key.DOWN):
            direction = direction + engine.Vector2.down()
        if kb.is_pressed(engine.Key.A) or kb.is_pressed(engine.Key.LEFT):
            direction = direction + engine.Vector2.left()
        if kb.is_pressed(engine.Key.D) or kb.is_pressed(engine.Key.RIGHT):
            direction = direction + engine.Vector2.right()

        # 대각선 이동 시 속도 정규화
        if direction.magnitude > 0:
            direction = direction.normalized
            self.transform.translate(direction * self.speed * dt)
```

> **정규화가 필요한 이유**: 대각선 입력(예: 오른쪽+아래)이면 방향 벡터의 크기가 `sqrt(2) = 1.414`가 되어, 대각선 이동이 직선보다 약 41% 빨라진다. `normalized`로 크기를 1로 만들면 모든 방향에서 동일한 속도가 보장된다.

### 2. 사격 (쿨다운 포함)

```python
class Shooter(engine.Component):
    def on_start(self):
        self.fire_cooldown = 0.0
        self.fire_rate = 0.2  # 초당 5발

    def on_update(self, dt):
        kb = engine.current_app().keyboard

        # 쿨다운 감소
        self.fire_cooldown = max(0, self.fire_cooldown - dt)

        # 스페이스바를 누르고 있으면 연사
        if kb.is_pressed(engine.Key.SPACE) and self.fire_cooldown <= 0:
            self.fire()
            self.fire_cooldown = self.fire_rate

    def fire(self):
        # 총알 엔티티 생성
        bullet = engine.Entity("Bullet")
        bullet.position = self.position.copy()
        bullet.add_component(BulletMovement())
        bullet.add_component(BulletRenderer())
        self.entity._world.add(bullet)
```

### 3. 마우스로 조준하여 사격

```python
class AimShooter(engine.Component):
    def on_update(self, dt):
        app = engine.current_app()
        mouse = app.mouse

        # 마우스를 향해 회전
        self.transform.look_at(mouse.position)

        # 마우스 왼쪽 클릭으로 사격
        if mouse.is_just_pressed(engine.MouseButton.LEFT):
            direction = (mouse.position - self.position).normalized
            self.fire(direction)

    def fire(self, direction):
        bullet = engine.Entity("Bullet")
        bullet.position = self.position.copy()
        bullet.transform.look_at(self.position + direction)
        bullet.add_component(BulletMovement())
        self.entity._world.add(bullet)
```

### 4. 메뉴 탐색

```python
class MenuNavigation(engine.Component):
    def on_start(self):
        self.options = ["시작", "설정", "종료"]
        self.selected = 0

    def on_update(self, dt):
        kb = engine.current_app().keyboard

        # 위/아래로 선택 이동 (just_pressed로 한 번만)
        if kb.is_just_pressed(engine.Key.UP):
            self.selected = (self.selected - 1) % len(self.options)
        if kb.is_just_pressed(engine.Key.DOWN):
            self.selected = (self.selected + 1) % len(self.options)

        # Enter로 확인
        if kb.is_just_pressed(engine.Key.RETURN):
            self.confirm(self.options[self.selected])

    def confirm(self, option):
        if option == "종료":
            engine.current_app().quit()

    def on_draw(self, renderer):
        for i, option in enumerate(self.options):
            y = 200 + i * 40
            color = engine.Color.YELLOW if i == self.selected else engine.Color.WHITE
            # 선택된 항목에 표시
            if i == self.selected:
                renderer.draw_rect(190, y - 2, 220, 28, engine.Color.DARK_GRAY)
            renderer.draw_rect(200, y, 200, 24, color, filled=False)
```

> **is_pressed vs is_just_pressed 선택 기준**:
> - 연속 동작 (이동, 연사): `is_pressed` 사용
> - 단발 동작 (점프, 메뉴 선택, 한 발 사격): `is_just_pressed` 사용
> - 해제 시 동작 (차징 해제, 드래그 종료): `is_just_released` 사용

### 5. 수정자 키 조합

```python
class ModifierKeys(engine.Component):
    def on_update(self, dt):
        kb = engine.current_app().keyboard

        # Shift + 이동 = 달리기
        if kb.is_pressed(engine.Key.LSHIFT) and kb.is_pressed(engine.Key.D):
            move_speed = self.run_speed  # 빠른 속도
        else:
            move_speed = self.walk_speed  # 보통 속도

        # Ctrl + Z = 되돌리기 (한 번만)
        if kb.is_pressed(engine.Key.LCTRL) and kb.is_just_pressed(engine.Key.Z):
            self.undo()
```

### 6. 마우스 드래그

```python
class DragHandler(engine.Component):
    def on_start(self):
        self.dragging = False
        self.drag_start = engine.Vector2.zero()

    def on_update(self, dt):
        mouse = engine.current_app().mouse

        if mouse.is_just_pressed(engine.MouseButton.LEFT):
            self.dragging = True
            self.drag_start = mouse.position.copy()

        if self.dragging and mouse.is_pressed(engine.MouseButton.LEFT):
            # 드래그 중: 시작점에서 현재 위치까지
            current = mouse.position
            delta = current - self.drag_start
            # delta를 사용한 로직...

        if mouse.is_just_released(engine.MouseButton.LEFT):
            self.dragging = False
```

---

## 프레임별 입력 상태 전체 흐름

```
Game.run() 프레임 시작
    |
    v
app.poll_events()     <-- Game.run()이 자동으로 호출
    |
    +-- keyboard.update()
    |   (previous <- current 복사)
    |
    +-- mouse.update()
    |   (previous <- current 복사, scroll_delta = 0)
    |
    +-- SDL_PollEvent 루프
    |   +-- KEYDOWN: current.add(key)
    |   +-- KEYUP:   current.discard(key)
    |   +-- MOUSEMOTION: position 갱신
    |   +-- MOUSEBUTTONDOWN: current.add(button)
    |   +-- MOUSEBUTTONUP: current.discard(button)
    |   +-- MOUSEWHEEL: scroll_delta += wheel.y
    |
    v
Scene.update(dt)
    |
    +-- Component.on_start() (새 컴포넌트)
    +-- Component.on_update(dt)      <-- 여기서 입력 조회
    +-- Component.on_late_update(dt)
    |
    v
Scene.draw(renderer)
    |
    +-- Component.on_draw(renderer)
    |
    v
프레임 끝
```

> **참고**: Component의 `on_update`에서 입력을 조회하면 항상 현재 프레임의 최신 입력 상태를 얻을 수 있다. `Game.run()`이 on_update 호출 전에 `poll_events()`를 보장하기 때문이다.

---

## 다음 단계

- [렌더링](rendering.md) -- 입력에 반응하여 화면에 그리는 방법.
- [ECS 시스템](ecs.md) -- Component에서 입력을 처리하는 패턴.
- [씬 관리](scene.md) -- 메뉴와 게임 화면 간 전환.
