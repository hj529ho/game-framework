# 렌더링 (renderer)

렌더링 모듈은 **지연 드로우 큐(Deferred Draw Queue)** 방식으로 동작한다. 그리기 함수를 호출하면 즉시 화면에 그려지지 않고, 내부 큐에 명령이 저장된다. 프레임이 끝날 때 큐를 레이어 순서대로 정렬하여 한 번에 실행한다.

```python
from engine import Renderer, Color
```

> **참고**: `Game.run()`이 매 프레임 `begin_frame()`과 `end_frame()`을 자동으로 호출한다. Component의 `on_draw(renderer)` 훅에서는 그리기 명령만 호출하면 된다.

---

## Renderer

### 지연 드로우 큐 개념

전통적인 즉시 모드 렌더링과 이 엔진의 지연 렌더링을 비교해 보자.

```
즉시 모드 (Immediate Mode):
  draw_rect(배경)     --> 즉시 화면에 그림
  draw_rect(캐릭터)   --> 즉시 화면에 그림  (배경 위에)
  draw_rect(UI)       --> 즉시 화면에 그림  (캐릭터 위에)

  문제: 호출 순서가 곧 렌더링 순서. 코드 구조에 따라 순서가 결정됨.

지연 모드 (Deferred Mode, 이 엔진):
  draw_rect(UI,       layer=10)  --> 큐에 저장
  draw_rect(캐릭터,   layer=0)   --> 큐에 저장
  draw_rect(배경,     layer=-1)  --> 큐에 저장
  end_frame() -->
    1. layer 기준 정렬: 배경(-1), 캐릭터(0), UI(10)
    2. 정렬된 순서대로 실행
    3. SDL_RenderPresent

  장점: 호출 순서와 무관하게, layer 값으로 앞뒤 관계 결정.
```

### 드로우 큐의 내부 구조

큐의 각 항목은 `(layer, order, draw_fn)`의 3가지 값으로 구성된다.

| 필드 | 설명 |
|---|---|
| `layer` | 레이어 번호. 작을수록 먼저 그려짐 (뒤쪽) |
| `order` | 같은 레이어 내 호출 순서. 자동 증가 |
| `draw_fn` | 실제 SDL2 렌더링 함수를 호출하는 클로저 |

정렬 기준: `(layer, order)` 오름차순. 즉, 레이어가 같으면 먼저 호출된 것이 먼저 그려진다.

---

## begin_frame / end_frame 생명주기

매 프레임의 렌더링은 `begin_frame()`으로 시작하고 `end_frame()`으로 끝난다. `Game.run()`이 이 두 호출을 자동으로 관리하며, Component의 `on_draw` 훅은 그 사이에 실행된다.

```
Game.run() 내부:
  app.renderer.begin_frame()    # (1) 시작
  scenes.draw(app.renderer)     # (2) Component.on_draw() 호출 -> 큐에 추가
  app.renderer.end_frame()      # (3) 실행 및 표시
```

### begin_frame()

```
begin_frame() 내부 동작:
  1. 드로우 큐 초기화 (이전 프레임의 명령 제거)
  2. order 카운터 초기화 (0부터 다시 시작)
  3. clear_color로 SDL 렌더러의 그리기 색상 설정
  4. SDL_RenderClear로 화면 전체를 clear_color로 채움
```

### end_frame()

```
end_frame() 내부 동작:
  1. 드로우 큐를 (layer, order) 기준으로 정렬
  2. 정렬된 순서대로 각 draw_fn() 실행
     - SDL_SetRenderDrawColor로 색상 설정
     - SDL_RenderFillRect, SDL_RenderDrawLine 등 실행
  3. SDL_RenderPresent로 백 버퍼를 화면에 표시
```

### 전체 흐름 다이어그램

```
begin_frame()
    |
    +-- 큐 = []
    +-- 화면 클리어
    |
    v
Component A: on_draw(renderer)
  draw_rect(x=10, ..., layer=0)    --> 큐 = [(0, 0, fn_a)]
Component B: on_draw(renderer)
  draw_rect(x=50, ..., layer=1)    --> 큐 = [(0, 0, fn_a), (1, 1, fn_b)]
Component C: on_draw(renderer)
  draw_line(..., layer=-1)          --> 큐 = [(0, 0, fn_a), (1, 1, fn_b), (-1, 2, fn_c)]
  draw_rect(x=90, ..., layer=0)    --> 큐 = [(0, 0, fn_a), (1, 1, fn_b), (-1, 2, fn_c), (0, 3, fn_d)]
    |
    v
end_frame()
    |
    +-- 정렬: [(-1, 2, fn_c), (0, 0, fn_a), (0, 3, fn_d), (1, 1, fn_b)]
    +-- fn_c() 실행 (layer=-1, 선)
    +-- fn_a() 실행 (layer=0, 첫 번째 사각형)
    +-- fn_d() 실행 (layer=0, 네 번째 사각형)
    +-- fn_b() 실행 (layer=1, 두 번째 사각형)
    +-- SDL_RenderPresent
```

---

## 그리기 프리미티브

### draw_rect (사각형)

```python
renderer.draw_rect(
    x: float, y: float,          # 좌상단 좌표
    width: float, height: float,  # 크기
    color: Color,                 # 색상
    filled: bool = True,          # True=채우기, False=외곽선만
    layer: int = 0,               # 레이어
)
```

예제 (Component의 on_draw 내부):

```python
class BoxRenderer(engine.Component):
    def on_awake(self):
        self.color = engine.Color.BLUE
        self.size = 64

    def on_draw(self, renderer):
        p = self.position
        half = self.size / 2

        # 채워진 파란색 사각형
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size, self.color)

        # 빨간색 외곽선 사각형
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size,
                           engine.Color.RED, filled=False)

        # 반투명 초록색 사각형
        green_transparent = engine.Color.GREEN.with_alpha(128)
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size,
                           green_transparent)
```

```
  filled=True           filled=False
  +----------+          +----------+
  |//////////|          |          |
  |//////////|          |          |
  |//////////|          |          |
  +----------+          +----------+
  내부가 채워짐          외곽선만 표시
```

### draw_line (선)

```python
renderer.draw_line(
    start: Vector2,    # 시작점
    end: Vector2,      # 끝점
    color: Color,      # 색상
    layer: int = 0,    # 레이어
)
```

예제:

```python
class GridRenderer(engine.Component):
    """배경 격자를 그리는 컴포넌트."""

    def on_draw(self, renderer):
        # 격자 그리기 (배경 레이어)
        for x in range(0, 800, 50):
            renderer.draw_line(
                engine.Vector2(x, 0),
                engine.Vector2(x, 600),
                engine.Color.DARK_GRAY,
                layer=-1,
            )
        for y in range(0, 600, 50):
            renderer.draw_line(
                engine.Vector2(0, y),
                engine.Vector2(800, y),
                engine.Color.DARK_GRAY,
                layer=-1,
            )
```

### draw_texture (텍스처)

```python
renderer.draw_texture(
    texture: SDL_Texture,        # SDL2 텍스처 핸들
    x: float, y: float,         # 좌상단 좌표
    width: int | None = None,   # None이면 텍스처 원본 크기
    height: int | None = None,  # None이면 텍스처 원본 크기
    angle: float = 0.0,         # 회전 각도 (도)
    layer: int = 0,             # 레이어
)
```

예제:

```python
class SpriteRenderer(engine.Component):
    def on_awake(self):
        self.texture = None  # 외부에서 설정
        self.width = 64
        self.height = 64

    def on_draw(self, renderer):
        if self.texture:
            p = self.position
            renderer.draw_texture(
                self.texture,
                p.x - self.width / 2, p.y - self.height / 2,
                width=self.width, height=self.height,
                angle=self.entity.rotation,
            )
```

> **참고**: `width`나 `height`를 `None`으로 지정하면 `SDL_QueryTexture`를 호출하여 텍스처의 원본 크기를 자동으로 가져온다.

---

## 레이어 시스템과 z-ordering

레이어는 정수 값으로, **작은 숫자가 먼저 그려진다** (화면에서 뒤쪽에 위치).

```
레이어 배치 예시:

layer = -10   배경 이미지
layer = -1    타일맵
layer = 0     게임 오브젝트 (기본값)
layer = 1     전경 효과
layer = 5     파티클
layer = 10    UI 요소
layer = 100   디버그 오버레이

화면에 보이는 순서 (아래에서 위로):
+----------------------------------+
| 디버그 오버레이 (layer=100)       |  <-- 가장 위
| UI 요소 (layer=10)               |
| 파티클 (layer=5)                 |
| 전경 효과 (layer=1)              |
| 게임 오브젝트 (layer=0)          |
| 타일맵 (layer=-1)               |
| 배경 이미지 (layer=-10)          |  <-- 가장 뒤
+----------------------------------+
```

### 같은 레이어 내 순서

같은 레이어의 그리기 명령은 **호출 순서(order)**가 유지된다. 즉, 먼저 호출한 것이 먼저 그려진다 (뒤쪽에 위치).

```python
# Component의 on_draw에서 같은 layer=0일 때
class ShadowedBox(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        # 그림자 (먼저 그려짐 = 뒤)
        renderer.draw_rect(p.x - 14, p.y - 10, 32, 32, engine.Color.DARK_GRAY)
        # 본체 (나중에 그려짐 = 앞)
        renderer.draw_rect(p.x - 16, p.y - 16, 32, 32, engine.Color.BLUE)
```

```
결과:
  +------+
  | DARK +------+
  |GRAY  | BLUE |   BLUE가 DARK_GRAY 위에 겹쳐서 보임
  +------+      |
         +------+
```

### 레이어 사용 전략

```python
# 상수로 레이어를 정의하면 관리가 편하다
class Layers:
    BACKGROUND = -10
    TILES = -1
    ENTITIES = 0
    EFFECTS = 5
    UI = 10
    DEBUG = 100

# Component의 on_draw에서 사용
class BackgroundRenderer(engine.Component):
    def on_draw(self, renderer):
        renderer.draw_rect(0, 0, 800, 600, sky_color, layer=Layers.BACKGROUND)

class PlayerRenderer(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(p.x - 16, p.y - 16, 32, 32, engine.Color.BLUE,
                           layer=Layers.ENTITIES)

class HUDRenderer(engine.Component):
    def on_draw(self, renderer):
        renderer.draw_rect(10, 10, 200, 20, engine.Color.RED, layer=Layers.UI)
```

---

## Color 클래스

`Color`는 RGBA 색상을 나타내며, SDL2에 의존하지 않는 순수 Python 클래스이다.

### 생성

```python
from engine import Color

# RGB (알파는 기본 255 = 불투명)
red = Color(255, 0, 0)

# RGBA
semi_transparent = Color(255, 0, 0, 128)  # 반투명 빨강
```

### 필드

| 필드 | 범위 | 설명 |
|---|---|---|
| `r` | 0~255 | 빨강 |
| `g` | 0~255 | 초록 |
| `b` | 0~255 | 파랑 |
| `a` | 0~255 | 알파 (0=투명, 255=불투명) |

### 메서드

#### to_tuple

```python
color = Color(255, 128, 0, 200)
print(color.to_tuple())  # (255, 128, 0, 200)
```

#### lerp (색상 보간)

두 색상 사이를 `t` 비율로 보간한다. 그라디언트나 색상 전환 효과에 유용하다.

```python
red = Color.RED
blue = Color.BLUE

mid_color = red.lerp(blue, 0.5)   # 보라색 계열
print(mid_color)                    # Color(127, 0, 127, 255)
```

```
t=0.0        t=0.5        t=1.0
  RED  --------> ? -------> BLUE
(255,0,0)   (127,0,127)   (0,0,255)
```

#### with_alpha

알파값만 변경한 새 색상을 반환한다.

```python
solid_red = Color.RED             # (255, 0, 0, 255)
ghost_red = Color.RED.with_alpha(64)  # (255, 0, 0, 64)  -- 매우 투명
```

### 사전 정의된 색상 상수

| 상수 | 값 (R, G, B, A) | 시각적 설명 |
|---|---|---|
| `Color.WHITE` | (255, 255, 255, 255) | 흰색 |
| `Color.BLACK` | (0, 0, 0, 255) | 검은색 |
| `Color.RED` | (255, 0, 0, 255) | 빨간색 |
| `Color.GREEN` | (0, 255, 0, 255) | 초록색 |
| `Color.BLUE` | (0, 0, 255, 255) | 파란색 |
| `Color.YELLOW` | (255, 255, 0, 255) | 노란색 |
| `Color.CYAN` | (0, 255, 255, 255) | 청록색 |
| `Color.MAGENTA` | (255, 0, 255, 255) | 자홍색 |
| `Color.ORANGE` | (255, 165, 0, 255) | 주황색 |
| `Color.GRAY` | (128, 128, 128, 255) | 회색 |
| `Color.DARK_GRAY` | (64, 64, 64, 255) | 진한 회색 |
| `Color.LIGHT_GRAY` | (192, 192, 192, 255) | 밝은 회색 |
| `Color.TRANSPARENT` | (0, 0, 0, 0) | 완전 투명 |

---

## clear_color (배경색)

`begin_frame()`에서 화면을 지울 때 사용되는 배경색이다.

```python
# Game 생성 시 설정
game = engine.Game(title="My Game", clear_color=engine.Color(20, 20, 40))

# 실행 중 Component에서 동적 변경
class DynamicBackground(engine.Component):
    def on_update(self, dt):
        engine.current_app().renderer.clear_color = engine.Color(0, 0, 0)
```

---

## 실전 예제: Component 기반 렌더링

```python
import engine

# --- Components ---

class PlayerMovement(engine.Component):
    def on_start(self):
        self.speed = 200.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
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


class PlayerRenderer(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        # 그림자 (layer=0, 먼저 그려짐)
        renderer.draw_rect(p.x - 14, p.y - 10, 32, 32, engine.Color.DARK_GRAY, layer=0)
        # 플레이어 (layer=1, 그림자 위에)
        renderer.draw_rect(p.x - 16, p.y - 16, 32, 32, engine.Color.CYAN, layer=1)


class GridRenderer(engine.Component):
    """배경 격자를 그리는 컴포넌트."""

    def on_draw(self, renderer):
        for x in range(0, 800, 40):
            renderer.draw_line(
                engine.Vector2(x, 0), engine.Vector2(x, 600),
                engine.Color.DARK_GRAY, layer=-1,
            )
        for y in range(0, 600, 40):
            renderer.draw_line(
                engine.Vector2(0, y), engine.Vector2(800, y),
                engine.Color.DARK_GRAY, layer=-1,
            )


class PositionBar(engine.Component):
    """플레이어 x 위치를 시각화하는 UI 바."""

    def on_start(self):
        self.player = None

    def on_draw(self, renderer):
        if self.player:
            bar_width = int((self.player.position.x / 800) * 200)
            renderer.draw_rect(10, 10, 200, 8, engine.Color.DARK_GRAY, layer=10)
            renderer.draw_rect(10, 10, bar_width, 8, engine.Color.GREEN, layer=10)


# --- Scene ---

class GameScene(engine.Scene):
    def on_enter(self):
        # 배경 격자
        grid = engine.Entity("Grid")
        grid.add_component(GridRenderer())
        self.add(grid)

        # 플레이어
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_component(PlayerMovement())
        player.add_component(PlayerRenderer())
        self.add(player)

        # UI
        hud = engine.Entity("HUD")
        bar = hud.add_component(PositionBar())
        bar.player = player
        self.add(hud)

    def on_exit(self):
        self.world.clear()


# --- Run ---

game = engine.Game(title="Rendering Demo", width=800, height=600)
game.run(GameScene())
```

이 예제에서 레이어의 효과:
- **layer=-1**: 격자가 모든 것 뒤에 그려진다.
- **layer=0**: 플레이어의 그림자.
- **layer=1**: 플레이어가 그림자 위에 그려진다.
- **layer=10**: UI가 모든 것 위에 그려진다.

---

## 다음 단계

- [ECS 시스템](ecs.md) -- Component의 `on_draw` 메서드에서 Renderer를 사용하는 방법.
- [씬 관리](scene.md) -- 씬별로 분리된 렌더링 관리.
- [수학 모듈](math.md) -- Vector2, Rect 등 좌표 관련 타입.
