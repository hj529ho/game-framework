# 수학 모듈 (math)

수학 모듈은 2D 게임에 필요한 벡터 연산, 충돌 프리미티브, 변환(Transform), 보간 유틸리티를 제공한다. 이 모듈은 다른 엔진 모듈에 의존하지 않으며, 순수 Python 수학 연산만으로 구성되어 있다.

```python
from engine import Vector2, Rect, Circle, Transform2D
from engine.math import utils
```

---

## Vector2

`Vector2`는 2D 벡터를 나타내는 클래스로, 이 엔진에서 가장 많이 사용되는 타입이다. 위치, 방향, 속도, 크기 등을 표현하는 데 사용된다.

### 생성

```python
from engine import Vector2

# 기본 생성
v = Vector2(3.0, 4.0)       # x=3, y=4
v_zero = Vector2()           # x=0, y=0 (기본값)

# 정적 생성자
Vector2.zero()               # (0, 0)
Vector2.one()                # (1, 1)
Vector2.up()                 # (0, -1)  -- 화면 좌표계: 위쪽이 -y
Vector2.down()               # (0, 1)
Vector2.left()               # (-1, 0)
Vector2.right()              # (1, 0)
Vector2.from_angle(45)       # 45도 방향의 단위 벡터
```

> **화면 좌표계 주의**: 일반적인 수학 좌표계와 달리, 화면 좌표계에서는 y축이 아래로 증가한다. 따라서 `Vector2.up()`은 `(0, -1)`이다.

```
수학 좌표계               화면 좌표계 (이 엔진)
    y+                    (0,0) -----> x+
    |                       |
    |                       |
    +-----> x+              v
                           y+

  up = (0, 1)             up = (0, -1)
```

### 필드와 인덱스 접근

```python
v = Vector2(3.0, 4.0)

# 필드 접근
print(v.x)    # 3.0
print(v.y)    # 4.0

# 인덱스 접근
print(v[0])   # 3.0 (= x)
print(v[1])   # 4.0 (= y)

# 튜플 언패킹
x, y = v      # x=3.0, y=4.0
```

### 산술 연산

```python
a = Vector2(1, 2)
b = Vector2(3, 4)

# 벡터 + 벡터
c = a + b          # Vector2(4, 6)

# 벡터 - 벡터
d = a - b          # Vector2(-2, -2)

# 벡터 * 스칼라
e = a * 3          # Vector2(3, 6)

# 스칼라 * 벡터 (교환 법칙 성립)
f = 3 * a          # Vector2(3, 6)

# 벡터 / 스칼라
g = a / 2          # Vector2(0.5, 1.0)

# 부정 (negation)
h = -a             # Vector2(-1, -2)
```

### 속성 (Properties)

```python
v = Vector2(3.0, 4.0)

# 크기 (magnitude, length)
print(v.magnitude)       # 5.0  (= sqrt(3^2 + 4^2))

# 크기의 제곱 (sqrt 연산 생략, 성능 최적화용)
print(v.sqr_magnitude)   # 25.0  (= 3^2 + 4^2)

# 정규화 (단위 벡터: 크기가 1인 같은 방향 벡터)
print(v.normalized)      # Vector2(0.6, 0.8)
```

**`sqr_magnitude` 활용 팁**: 두 벡터 간 거리를 비교할 때, `distance_to`보다 `sqr_magnitude`를 사용하면 sqrt 연산을 피할 수 있어 성능에 유리하다.

```python
# 거리 비교 (비효율적)
if a.distance_to(b) < 100:
    ...

# 거리 비교 (효율적: sqrt를 피함)
if (a - b).sqr_magnitude < 100 * 100:
    ...
```

### 메서드

#### dot (내적)

두 벡터의 내적을 계산한다. 두 벡터가 같은 방향을 가리키면 양수, 수직이면 0, 반대 방향이면 음수이다.

```python
a = Vector2(1, 0)
b = Vector2(0, 1)
c = Vector2(-1, 0)

print(a.dot(a))  # 1.0  (같은 방향)
print(a.dot(b))  # 0.0  (수직)
print(a.dot(c))  # -1.0 (반대 방향)
```

```
        b (0,1)
        ^
        |
        |  dot = 0
 c <----+----> a (1,0)
(-1,0)  |
        |  dot = 1 (a.dot(a))
     dot = -1
     (a.dot(c))
```

#### cross (2D 외적)

2D 외적은 스칼라 값을 반환한다. 두 벡터로 이루어진 평행사변형의 부호 있는 넓이를 나타낸다.

```python
a = Vector2(1, 0)
b = Vector2(0, 1)

print(a.cross(b))   #  1.0 (b가 a의 왼쪽)
print(b.cross(a))   # -1.0 (a가 b의 오른쪽)
```

#### distance_to (거리)

```python
a = Vector2(0, 0)
b = Vector2(3, 4)

print(a.distance_to(b))  # 5.0
```

#### angle_to (각도)

한 점에서 다른 점을 향하는 각도(도 단위)를 반환한다.

```python
origin = Vector2(0, 0)
target = Vector2(1, 0)
print(origin.angle_to(target))  # 0.0  (오른쪽)

target = Vector2(0, 1)
print(origin.angle_to(target))  # 90.0  (아래쪽, 화면 좌표계)

target = Vector2(-1, 0)
print(origin.angle_to(target))  # 180.0  (왼쪽)
```

#### lerp (선형 보간)

두 벡터 사이를 `t` 비율로 보간한다. `t=0`이면 자기 자신, `t=1`이면 상대 벡터를 반환한다.

```python
a = Vector2(0, 0)
b = Vector2(100, 0)

print(a.lerp(b, 0.0))   # Vector2(0, 0)
print(a.lerp(b, 0.25))  # Vector2(25, 0)
print(a.lerp(b, 0.5))   # Vector2(50, 0)
print(a.lerp(b, 1.0))   # Vector2(100, 0)
```

```
t=0.0     t=0.25    t=0.5     t=0.75    t=1.0
  a---------+---------+---------+---------b
 (0,0)    (25,0)   (50,0)   (75,0)    (100,0)
```

게임에서의 활용: 부드러운 카메라 추적, 오브젝트 이동 애니메이션 등.

```python
# Component에서 카메라가 플레이어를 부드럽게 추적
class CameraFollow(engine.Component):
    def on_late_update(self, dt):
        if self.target:
            self.position = self.position.lerp(self.target.position, 5.0 * dt)
```

#### rotate (회전)

원점을 중심으로 주어진 각도만큼 회전한 벡터를 반환한다.

```python
v = Vector2(1, 0)  # 오른쪽 방향

print(v.rotate(90))    # Vector2(0, 1)   -- 90도 회전 (아래쪽)
print(v.rotate(180))   # Vector2(-1, 0)  -- 180도 회전 (왼쪽)
print(v.rotate(-90))   # Vector2(0, -1)  -- -90도 회전 (위쪽)
```

#### copy (복사)

```python
a = Vector2(1, 2)
b = a.copy()
b.x = 99
print(a)  # Vector2(1, 2)  -- 원본은 변경되지 않음
```

### 비교

`==` 연산자는 `math.isclose`를 사용하여 근사 비교를 수행한다. 부동소수점 오차로 인한 문제를 방지한다.

```python
a = Vector2(1.0, 2.0)
b = Vector2(1.0000000001, 2.0)
print(a == b)  # True (근사 비교)
```

### 메모리 효율성

`Vector2`는 `__slots__`를 사용하여 일반 Python 객체보다 메모리를 적게 사용한다. 수천 개의 벡터를 생성해도 성능 문제가 적다.

---

## Rect

`Rect`는 축 정렬 바운딩 박스(Axis-Aligned Bounding Box, AABB)를 나타낸다. 충돌 검사, 영역 계산, 화면 영역 관리에 사용된다.

### 생성

```python
from engine import Rect

# (x, y, width, height)
r = Rect(100, 50, 200, 150)
```

```
       100      300
    (x) |--------|  (x + width)
   50 --+--------+
  (y)   |        |
        |  200   |  height=150
        | x 150  |
  200 --+--------+
  (y+h)
```

### 속성

```python
r = Rect(100, 50, 200, 150)

# 가장자리
print(r.left)       # 100.0  (= x)
print(r.right)      # 300.0  (= x + width)
print(r.top)        # 50.0   (= y)
print(r.bottom)     # 200.0  (= y + height)

# 중심점
print(r.center)     # Vector2(200, 125)

# 좌상단 점
print(r.top_left)   # Vector2(100, 50)

# 크기
print(r.size)       # Vector2(200, 150)
```

### 점 포함 검사 (contains_point)

주어진 점이 사각형 내부에 있는지 검사한다 (경계 포함).

```python
r = Rect(0, 0, 100, 100)

print(r.contains_point(Vector2(50, 50)))    # True  (내부)
print(r.contains_point(Vector2(0, 0)))      # True  (경계)
print(r.contains_point(Vector2(100, 100)))  # True  (경계)
print(r.contains_point(Vector2(101, 50)))   # False (외부)
```

### 겹침 검사 (overlaps)

두 사각형이 겹치는지 검사한다.

```python
a = Rect(0, 0, 100, 100)
b = Rect(50, 50, 100, 100)
c = Rect(200, 200, 50, 50)

print(a.overlaps(b))  # True  (겹침)
print(a.overlaps(c))  # False (겹치지 않음)
```

```
  a         b가 겹치는 경우            a와 c가 안 겹치는 경우
+-----+                              +-----+
|  a  |                              |  a  |
|  +--+--+                           +-----+
+--+--+  |                                      +---+
   | b   |                                      | c |
   +-----+                                      +---+
```

### 교차 영역 (intersection)

두 사각형이 겹치는 영역을 `Rect`로 반환한다. 겹치지 않으면 `None`을 반환한다.

```python
a = Rect(0, 0, 100, 100)
b = Rect(50, 50, 100, 100)

inter = a.intersection(b)
print(inter)  # Rect(50, 50, 50, 50)

c = Rect(200, 200, 50, 50)
print(a.intersection(c))  # None
```

### 확장 (expanded)

사각형을 모든 방향으로 `amount`만큼 확장한다.

```python
r = Rect(100, 100, 50, 50)
expanded = r.expanded(10)
print(expanded)  # Rect(90, 90, 70, 70)
```

```
  확장 전                    확장 후 (amount=10)
  +------+                +-----------+
  |      | 50x50          |           | 70x70
  +------+                |  +------+ |
                          |  |      | |
                          |  +------+ |
                          +-----------+
                          ^10px 여백^
```

### 튜플 변환

```python
r = Rect(10, 20, 30, 40)
print(r.to_tuple())  # (10.0, 20.0, 30.0, 40.0)
```

---

## Circle

`Circle`은 원형 충돌 프리미티브이다. 중심점과 반지름으로 정의된다.

### 생성

```python
from engine import Circle, Vector2

c = Circle(center=Vector2(100, 100), radius=50)
```

### 점 포함 검사

```python
c = Circle(Vector2(100, 100), 50)

print(c.contains_point(Vector2(100, 100)))  # True  (중심)
print(c.contains_point(Vector2(120, 100)))  # True  (내부)
print(c.contains_point(Vector2(200, 100)))  # False (외부)
```

### 원-원 충돌 (overlaps_circle)

두 원이 겹치는지 검사한다. 두 중심 간 거리가 반지름의 합보다 작으면 겹친다.

```python
a = Circle(Vector2(0, 0), 50)
b = Circle(Vector2(80, 0), 50)
c = Circle(Vector2(200, 0), 50)

print(a.overlaps_circle(b))  # True  (거리 80 < 반지름합 100)
print(a.overlaps_circle(c))  # False (거리 200 > 반지름합 100)
```

```
       r=50      r=50
     +----+    +----+
    /  a   \  /  b   \     <-- 겹침 (거리 80 < 50+50)
   |   *   ||   *    |
    \      /  \      /
     +----+    +----+
  center     center
  (0,0)      (80,0)
```

### 원-사각형 충돌 (overlaps_rect)

원과 축 정렬 사각형(AABB)이 겹치는지 검사한다.

```python
c = Circle(Vector2(50, 50), 30)
r = Rect(70, 30, 60, 40)

print(c.overlaps_rect(r))  # True
```

내부 알고리즘: 원의 중심에서 사각형의 가장 가까운 점까지의 거리가 반지름보다 작은지 검사한다.

### 바운딩 박스 (get_bounds)

원을 감싸는 최소 AABB를 반환한다.

```python
c = Circle(Vector2(100, 100), 50)
bounds = c.get_bounds()
print(bounds)  # Rect(50, 50, 100, 100)
```

```
     +----------+
     | 바운딩   |
     |   /--\   |
     |  | *  |  |  * = center (100, 100)
     |   \--/   |    radius = 50
     |   박스   |
     +----------+
     (50,50)  (150,150)
```

---

## Transform2D

`Transform2D`는 위치(position), 회전(rotation), 크기(scale)를 하나로 묶은 변환 컨테이너이다. 모든 `Entity`에 자동으로 하나씩 부착된다. Component에서 `self.transform`으로 접근할 수 있다.

### 생성

```python
from engine import Transform2D, Vector2

# 기본값: position=(0,0), rotation=0, scale=(1,1)
t = Transform2D()

# 커스텀 값
t = Transform2D(
    position=Vector2(100, 200),
    rotation=45.0,              # 도 단위
    scale=Vector2(2.0, 2.0),   # 2배 크기
)
```

### 필드

| 필드 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `position` | `Vector2` | `(0, 0)` | 월드 위치 |
| `rotation` | `float` | `0.0` | 회전 각도 (도 단위) |
| `scale` | `Vector2` | `(1, 1)` | 크기 비율 |

### forward 속성

현재 회전 방향의 단위 벡터를 반환한다.

```python
t = Transform2D(rotation=0)
print(t.forward)    # Vector2(1, 0) -- 오른쪽

t.rotation = 90
print(t.forward)    # Vector2(0, 1) -- 아래쪽 (화면 좌표계)

t.rotation = 180
print(t.forward)    # Vector2(-1, 0) -- 왼쪽
```

```
  rotation=0     rotation=90    rotation=180    rotation=270
      -->            |               <--             ^
   (1, 0)           v            (-1, 0)          (0, -1)
                  (0, 1)
```

### translate (이동)

현재 위치에 오프셋을 더한다.

```python
t = Transform2D(position=Vector2(100, 100))
t.translate(Vector2(50, 0))
print(t.position)  # Vector2(150, 100)
```

### look_at (회전)

특정 대상을 향하도록 회전을 설정한다.

```python
t = Transform2D(position=Vector2(100, 100))
t.look_at(Vector2(200, 100))
print(t.rotation)  # 0.0 (오른쪽)

t.look_at(Vector2(100, 200))
print(t.rotation)  # 90.0 (아래쪽)
```

### Entity/Component와의 관계

Entity는 `transform` 속성을 통해 Transform2D에 접근할 수 있다. Component에서는 `self.transform`과 `self.position` 단축 속성을 사용한다.

```python
# Entity에서 직접 접근
entity = engine.Entity("player")
entity.transform.position = engine.Vector2(100, 200)
entity.transform.rotation = 45.0

# Entity 단축 속성 (동일한 효과)
entity.position = engine.Vector2(100, 200)
entity.rotation = 45.0
entity.scale = engine.Vector2(2, 2)

# Component 내부에서 접근
class MyComponent(engine.Component):
    def on_update(self, dt):
        # self.transform = self.entity.transform
        self.transform.translate(engine.Vector2(10, 0) * dt)

        # self.position = self.entity.position (읽기/쓰기 가능)
        print(self.position)
```

---

## 유틸리티 함수 (utils)

`engine.math.utils` 모듈은 게임 개발에서 자주 사용되는 수학 유틸리티 함수를 제공한다.

```python
from engine.math import utils
```

### lerp (선형 보간)

```python
utils.lerp(a, b, t) -> float
```

두 값 사이를 `t` 비율(0~1)로 보간한다.

```python
print(utils.lerp(0, 100, 0.0))   # 0.0
print(utils.lerp(0, 100, 0.5))   # 50.0
print(utils.lerp(0, 100, 1.0))   # 100.0
print(utils.lerp(0, 100, 0.25))  # 25.0
```

```
t:    0.0       0.25      0.5       0.75      1.0
      |---------|---------|---------|---------|
값:   0         25        50        75       100
      a                                       b
```

활용 예: 체력바 애니메이션, 색상 전환, 부드러운 값 변화.

```python
# Component에서 체력바가 현재 값에서 목표 값으로 부드럽게 이동
class HealthBarSmooth(engine.Component):
    def on_start(self):
        self.displayed_hp = 100.0

    def on_update(self, dt):
        actual_hp = self.entity.get_component(Health).hp
        self.displayed_hp = utils.lerp(self.displayed_hp, actual_hp, 5.0 * dt)
```

### clamp (범위 제한)

```python
utils.clamp(value, min_val, max_val) -> float
```

값을 [min_val, max_val] 범위로 제한한다.

```python
print(utils.clamp(150, 0, 100))   # 100  (상한 초과 -> 상한으로)
print(utils.clamp(-50, 0, 100))   # 0    (하한 미만 -> 하한으로)
print(utils.clamp(50, 0, 100))    # 50   (범위 내 -> 그대로)
```

```
                          clamp(value, 0, 100)

     -50        0                   100        150
 -----*---------[====================]---------*-----
      |         ^                    ^         |
      +-------> 0 (clamped)    100 <-----------+
                     50 -> 50 (unchanged)
```

활용 예: 체력 제한, 위치를 화면 안에 제한.

```python
# Component에서 체력을 0~100 범위로 제한
class Health(engine.Component):
    def damage(self, amount):
        self.hp = utils.clamp(self.hp - amount, 0, self.max_hp)

# Component에서 플레이어를 화면 안에 가두기
class ScreenBounds(engine.Component):
    def on_late_update(self, dt):
        app = engine.current_app()
        x = utils.clamp(self.position.x, 16, app.width - 16)
        y = utils.clamp(self.position.y, 16, app.height - 16)
        self.position = engine.Vector2(x, y)
```

### remap (범위 변환)

```python
utils.remap(value, from_min, from_max, to_min, to_max) -> float
```

값을 한 범위에서 다른 범위로 변환한다.

```python
# 0~1 범위를 0~255 범위로 변환
print(utils.remap(0.5, 0, 1, 0, 255))    # 127.5

# 마우스 x좌표(0~800)를 각도(0~360)로 변환
print(utils.remap(400, 0, 800, 0, 360))   # 180.0

# 체력(0~100)을 바 너비(0~200)로 변환
print(utils.remap(75, 0, 100, 0, 200))    # 150.0
```

```
from 범위:   [0 --------- 0.5 --------- 1]
                            |
                            v  remap
to 범위:     [0 -------- 127.5 -------- 255]
```

### inverse_lerp (역 보간)

```python
utils.inverse_lerp(a, b, value) -> float
```

`lerp`의 역연산이다. 값이 `a`와 `b` 사이 어디에 위치하는지 비율(t)을 반환한다.

```python
print(utils.inverse_lerp(0, 100, 25))   # 0.25
print(utils.inverse_lerp(0, 100, 50))   # 0.5
print(utils.inverse_lerp(0, 100, 100))  # 1.0
```

활용 예: 진행률 계산, 정규화.

```python
# 체력 비율 계산
hp_ratio = utils.inverse_lerp(0, max_hp, current_hp)  # 0.0 ~ 1.0
```

### smoothstep (부드러운 보간)

```python
utils.smoothstep(edge0, edge1, x) -> float
```

선형 보간과 달리 시작과 끝에서 가속/감속하는 부드러운 보간 함수이다. Hermite 보간을 사용한다.

```python
print(utils.smoothstep(0, 1, 0.0))   # 0.0
print(utils.smoothstep(0, 1, 0.25))  # 0.15625
print(utils.smoothstep(0, 1, 0.5))   # 0.5
print(utils.smoothstep(0, 1, 0.75))  # 0.84375
print(utils.smoothstep(0, 1, 1.0))   # 1.0
```

lerp와 smoothstep의 비교:

```
출력값
 1.0 |               ...*****
     |            ..*      smoothstep (부드러운 곡선)
     |          .*
 0.5 |        .*..........
     |      .*          lerp (직선)
     |    .*
 0.0 |****
     +---+---+---+---+---+---> 입력값 (t)
     0  0.2  0.4  0.6  0.8  1.0

  lerp:       일정한 기울기로 변화
  smoothstep: 시작/끝에서 천천히, 중간에서 빠르게 변화
```

활용 예: 페이드 인/아웃, UI 애니메이션, 부드러운 전환 효과.

```python
# Component에서 씬 전환 페이드 효과
class FadeEffect(engine.Component):
    def on_start(self):
        self.elapsed = 0.0
        self.fade_duration = 1.0

    def on_update(self, dt):
        self.elapsed += dt
        fade_t = utils.smoothstep(0, self.fade_duration, self.elapsed)
        self.alpha = int(utils.lerp(0, 255, fade_t))
```

---

## 실전 활용 예제

### 적이 플레이어를 추적하는 컴포넌트

```python
import engine
from engine.math import utils

class ChasePlayer(engine.Component):
    def on_start(self):
        self.speed = 100.0

    def on_update(self, dt):
        # 같은 씬에서 "player" 태그가 있는 엔티티 찾기
        players = self.entity._world.find_by_tag("player")
        if not players:
            return

        player_pos = players[0].position

        # 플레이어를 향하는 방향 벡터
        to_player = player_pos - self.position
        distance = to_player.magnitude

        if distance > 5:  # 너무 가까우면 이동하지 않음
            direction = to_player.normalized
            self.transform.translate(direction * self.speed * dt)

        # 플레이어를 향해 회전
        self.transform.look_at(player_pos)


class EnemyRenderer(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(p.x - 12, p.y - 12, 24, 24, engine.Color.RED)
```

### 화면 경계 바운딩 컴포넌트

```python
class ScreenBounds(engine.Component):
    """엔티티를 화면 안에 가두는 컴포넌트."""

    def on_start(self):
        self.margin = 16

    def on_late_update(self, dt):
        app = engine.current_app()
        x = utils.clamp(self.position.x, self.margin, app.width - self.margin)
        y = utils.clamp(self.position.y, self.margin, app.height - self.margin)
        self.position = engine.Vector2(x, y)
```

### 충돌 검사

```python
from engine import Rect, Circle, Vector2

# Component의 on_update에서 충돌 검사
class CollisionChecker(engine.Component):
    def on_update(self, dt):
        my_pos = self.position

        # AABB 충돌
        my_rect = Rect(my_pos.x - 16, my_pos.y - 16, 32, 32)

        enemies = self.entity._world.find_by_tag("enemy")
        for enemy in enemies:
            e_pos = enemy.position
            enemy_rect = Rect(e_pos.x - 12, e_pos.y - 12, 24, 24)
            if my_rect.overlaps(enemy_rect):
                print("충돌!")

        # 원형 충돌 (더 자연스러운 판정)
        my_circle = Circle(my_pos, 16)
        for enemy in enemies:
            enemy_circle = Circle(enemy.position, 12)
            if my_circle.overlaps_circle(enemy_circle):
                print("충돌!")
```

---

## 다음 단계

- [입력 시스템](input.md) -- 키보드, 마우스 입력 처리 방법.
- [렌더링](rendering.md) -- 수학 타입을 사용하여 화면에 그리기.
- [ECS 시스템](ecs.md) -- Transform2D가 Entity/Component와 어떻게 연결되는지.
