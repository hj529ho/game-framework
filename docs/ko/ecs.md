# ECS 시스템 (Entity / Component / World)

ECS 모듈은 게임 오브젝트를 관리하는 핵심 시스템이다. 이 엔진은 **유니티 스타일 컴포넌트 패턴**을 사용한다. Entity는 순수 컨테이너(유니티의 GameObject)이며, 모든 게임 로직은 Component에서 구현한다.

```python
from engine import Entity, Component, World
```

---

## Entity

`Entity`는 게임 내 모든 객체의 컨테이너이다. 유니티의 `GameObject`와 같은 역할을 한다. Entity 자체에는 동작이 없으며, Transform과 Component 목록을 보유한다. 플레이어, 적, 총알, UI 등 모든 것은 Entity에 Component를 부착하여 만든다.

### 기본 구조

모든 Entity가 자동으로 갖는 것:

```
Entity (순수 컨테이너)
+-- id (int)              고유 식별자 (자동 증가)
+-- name (str)            이름 (기본: "Entity_{id}")
+-- transform (Transform2D)
|   +-- position (Vector2)   위치
|   +-- rotation (float)     회전 (도)
|   +-- scale (Vector2)      크기
+-- active (bool)         False면 모든 컴포넌트 훅이 스킵됨
+-- tags (set[str])       태그 집합
+-- components (list)     부착된 컴포넌트들
+-- parent (Entity|None)  부모 엔티티
+-- children (list)       자식 엔티티들
```

> **핵심**: Entity에는 `on_update`, `on_draw` 같은 생명주기 훅이 **없다**. 모든 동작은 Component에서 정의한다.

### 생성과 사용

```python
import engine

# 기본 생성
entity = engine.Entity()              # name = "Entity_1"
entity = engine.Entity("player")     # name = "player"

# 위치 설정 (단축 속성)
entity.position = engine.Vector2(100, 200)
entity.rotation = 45.0
entity.scale = engine.Vector2(2, 2)

# Transform 직접 접근 (동일한 효과)
entity.transform.position = engine.Vector2(100, 200)
entity.transform.rotation = 45.0
```

### 속성

| 속성 | 타입 | 쓰기 | 설명 |
|---|---|---|---|
| `id` | `int` | 불가 | 자동 증가 고유 ID |
| `name` | `str` | 가능 | 표시 이름 |
| `transform` | `Transform2D` | 불가 | 변환 객체 |
| `position` | `Vector2` | 가능 | transform.position 단축 |
| `rotation` | `float` | 가능 | transform.rotation 단축 (도) |
| `scale` | `Vector2` | 가능 | transform.scale 단축 |
| `active` | `bool` | 가능 | False면 모든 컴포넌트 훅 스킵 |
| `tags` | `set[str]` | 불가 | 읽기 전용 태그 집합 |
| `parent` | `Entity \| None` | 불가 | 부모 엔티티 |
| `children` | `list[Entity]` | 불가 | 자식 엔티티 복사본 |
| `components` | `list[Component]` | 불가 | 컴포넌트 복사본 |

### Component 관리 메서드

| 메서드 | 시그니처 | 반환 | 설명 |
|---|---|---|---|
| `add_component` | `(component: T) -> T` | `T` | 컴포넌트 부착. `on_awake()` 호출 |
| `get_component` | `(comp_type: type[T]) -> T \| None` | `T \| None` | 타입으로 첫 번째 컴포넌트 조회 |
| `get_components` | `(comp_type: type[T]) -> list[T]` | `list[T]` | 타입으로 모든 컴포넌트 조회 |
| `has_component` | `(comp_type: type[Component]) -> bool` | `bool` | 타입 존재 확인 |
| `remove_component` | `(component: Component) -> None` | `None` | 특정 인스턴스 제거. `on_destroy()` 호출 |
| `remove_components` | `(comp_type: type[Component]) -> None` | `None` | 타입의 모든 인스턴스 제거 |

### 태그 (Tags)

태그는 엔티티를 분류하고 검색하는 데 사용하는 문자열 집합이다.

```python
player = engine.Entity("Player")
player.add_tag("player")
player.add_tag("team_blue")

print(player.has_tag("player"))     # True
print(player.has_tag("enemy"))      # False
print(player.tags)                  # {"player", "team_blue"}
```

### 계층 구조 (Hierarchy)

엔티티에 자식 엔티티를 추가할 수 있다. 자식을 추가하면 같은 World에 자동으로 등록된다.

```python
ship = engine.Entity("ship")
turret = engine.Entity("turret")

ship.add_child(turret)  # turret이 ship의 자식이 됨

print(turret.parent)     # <Entity 'ship' ...>
print(ship.children)     # [<Entity 'turret' ...>]

ship.remove_child(turret)
print(turret.parent)     # None
```

> **참고**: 현재 버전에서 부모-자식 관계는 논리적 계층만 제공한다. 부모의 Transform이 자식에게 자동으로 상속되지는 않는다.

### Entity 구성 예제

```python
import engine

# Entity를 생성하고 Component를 부착하여 동작을 부여한다
player = engine.Entity("Player")
player.position = engine.Vector2(400, 300)
player.add_component(PlayerMovement())
player.add_component(PlayerRenderer())
player.add_component(Health(100))
player.add_tag("player")
scene.add(player)

# Entity는 Component가 없으면 아무 동작도 하지 않는다
empty = engine.Entity("EmptyContainer")
scene.add(empty)  # Transform만 존재, 업데이트/렌더링 없음
```

---

## Component

`Component`는 `Lifecycle`을 상속하는 기본 컴포넌트 클래스이다. 유니티의 `MonoBehaviour`와 같은 역할을 한다. Component를 상속하고 생명주기 훅을 오버라이드하여 게임 동작을 정의한다. Entity에 부착하여 사용한다.

### 생명주기 훅

| 훅 | 시그니처 | 호출 시점 |
|---|---|---|
| `on_awake` | `()` | `entity.add_component()` 호출 시 즉시 |
| `on_start` | `()` | 첫 `on_update` 전에 한 번 |
| `on_update` | `(dt: float)` | 매 프레임 |
| `on_late_update` | `(dt: float)` | 모든 `on_update` 호출 후 |
| `on_draw` | `(renderer: Renderer)` | 렌더링 단계 |
| `on_destroy` | `()` | 컴포넌트 제거 또는 엔티티 파괴 시 |

```
Entity에 Component 부착
    |
    v
on_awake()              <-- entity.add_component() 시점에 즉시
    |
    v (다음 world.update() 시점)
on_start()              <-- 첫 on_update 전에 한 번
    |
    v
+-- on_update(dt)       <-- 매 프레임
|   |
|   v
+-- on_late_update(dt)  <-- 모든 on_update 후
|   |
|   v
+-- on_draw(renderer)   <-- 렌더링 단계
|   |
|   v
+-- (반복)
    |
    v
on_destroy()            <-- 컴포넌트/엔티티 제거 시
```

### 속성 (단축키)

| 속성 | 타입 | 쓰기 | 설명 |
|---|---|---|---|
| `entity` | `Entity` | 불가 | 부착된 엔티티. 미부착 시 `RuntimeError` |
| `transform` | `Transform2D` | 불가 | `self.entity.transform` 단축 |
| `position` | `Vector2` | 가능 | `self.entity.position` 단축 |
| `enabled` | `bool` | 가능 | `False`면 생명주기 훅 스킵 (`on_destroy` 제외) |

### on_awake vs on_start

- **on_awake**: `entity.add_component()` 호출 시 즉시 실행된다. 자체 필드 초기화에 사용한다. 다른 컴포넌트가 아직 추가되지 않았을 수 있다.
- **on_start**: 첫 `on_update` 전에 실행된다. 이 시점에는 같은 엔티티의 모든 컴포넌트가 awake 상태이므로, 다른 컴포넌트에 의존하는 초기화에 사용한다.

```python
class WeaponSystem(engine.Component):
    def on_awake(self):
        # 자체 필드 초기화 (다른 컴포넌트에 의존하지 않음)
        self.damage = 10
        self.cooldown = 0.0

    def on_start(self):
        # 다른 컴포넌트 참조 (이 시점에 모두 awake)
        self.stats = self.entity.get_component(Stats)
        if self.stats:
            self.damage = self.stats.base_attack
```

### enabled 속성

`enabled`가 `False`인 컴포넌트는 `on_update`, `on_late_update`, `on_draw`가 호출되지 않는다. `on_destroy`는 `enabled`와 무관하게 항상 호출된다.

```python
class Damageable(engine.Component):
    def on_start(self):
        self.invincible_timer = 0.0

    def on_update(self, dt):
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                # 무적 해제: 깜빡임 컴포넌트 비활성화
                blink = self.entity.get_component(BlinkEffect)
                if blink:
                    blink.enabled = False

    def take_damage(self, amount):
        self.hp -= amount
        self.invincible_timer = 1.0
        # 깜빡임 컴포넌트 활성화
        blink = self.entity.get_component(BlinkEffect)
        if blink:
            blink.enabled = True
```

### Component 정의 예제

```python
import engine

class PlayerMovement(engine.Component):
    """키보드 이동을 처리하는 컴포넌트."""

    def on_start(self):
        self.speed = 200.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        direction = engine.Vector2.zero()
        if kb.is_pressed(engine.Key.RIGHT):
            direction = direction + engine.Vector2.right()
        if kb.is_pressed(engine.Key.LEFT):
            direction = direction + engine.Vector2.left()
        if kb.is_pressed(engine.Key.UP):
            direction = direction + engine.Vector2.up()
        if kb.is_pressed(engine.Key.DOWN):
            direction = direction + engine.Vector2.down()

        if direction.magnitude > 0:
            self.transform.translate(direction.normalized * self.speed * dt)


class SpriteRenderer(engine.Component):
    """사각형 스프라이트를 그리는 컴포넌트."""

    def on_awake(self):
        self.color = engine.Color.BLUE
        self.size = 32

    def on_draw(self, renderer):
        p = self.position
        half = self.size / 2
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size, self.color)


class Health(engine.Component):
    """체력을 관리하는 컴포넌트."""

    def on_awake(self):
        self.hp = 100
        self.max_hp = 100

    def damage(self, amount):
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            print(f"{self.entity.name} 사망!")

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    @property
    def is_alive(self):
        return self.hp > 0

    @property
    def ratio(self):
        return self.hp / self.max_hp


class HealthBarRenderer(engine.Component):
    """체력바를 그리는 컴포넌트. Health 컴포넌트가 필요하다."""

    def on_awake(self):
        self.bar_width = 40
        self.bar_height = 4
        self.offset_y = -24

    def on_draw(self, renderer):
        hp = self.entity.get_component(Health)
        if hp is None:
            return

        p = self.position
        bar_x = p.x - self.bar_width / 2
        bar_y = p.y + self.offset_y

        # 배경 (빨간색)
        renderer.draw_rect(bar_x, bar_y, self.bar_width, self.bar_height,
                           engine.Color.RED, layer=1)
        # 현재 체력 (초록색)
        renderer.draw_rect(bar_x, bar_y, self.bar_width * hp.ratio, self.bar_height,
                           engine.Color.GREEN, layer=1)
```

### Component 부착과 사용

```python
# Entity에 Component 부착
player = engine.Entity("Player")
player.position = engine.Vector2(400, 300)

# add_component는 부착된 컴포넌트를 반환한다
movement = player.add_component(PlayerMovement())
sprite = player.add_component(SpriteRenderer())
sprite.color = engine.Color.CYAN  # 속성 변경

player.add_component(Health())
player.add_component(HealthBarRenderer())
player.add_tag("player")

scene.add(player)

# Component 조회
hp = player.get_component(Health)
print(hp.hp)                           # 100
print(player.has_component(Health))    # True

# Component 제거
player.remove_component(movement)
print(player.has_component(PlayerMovement))  # False
```

---

## World

`World`는 Entity의 컨테이너이다. Entity를 추가/제거하고, 매 프레임 생명주기 훅 디스패치를 관리한다. Scene이 내부적으로 World를 소유한다.

### 지연 추가/제거 (Deferred Add/Remove)

World의 가장 중요한 특성은 **지연 처리**이다. Entity를 추가하거나 제거해도 즉시 반영되지 않는다. 다음 `update()` 호출 시점에 일괄 처리된다.

```
world.add(entity_a)      # 대기열에 추가 (아직 실제 목록에 없음)
world.add(entity_b)      # 대기열에 추가
world.remove(entity_c)   # 제거 대기열에 추가

world.update(dt)
  |
  +-- 1단계: 대기 중인 추가 처리
  |   +-- entity_a를 목록에 추가
  |   +-- entity_b를 목록에 추가
  |
  +-- 2단계: 새 컴포넌트의 on_start() 호출
  |
  +-- 3단계: 모든 활성 컴포넌트의 on_update(dt) 호출
  |
  +-- 4단계: 모든 활성 컴포넌트의 on_late_update(dt) 호출
  |
  +-- 5단계: 대기 중인 제거 처리
      +-- entity_c의 모든 컴포넌트에 on_destroy() 호출
      +-- 목록에서 제거
```

**왜 지연 처리를 하는가?**

게임 로직 실행 중에 엔티티 목록을 변경하면 반복(iteration) 중 목록이 변해서 오류가 발생할 수 있다. 예를 들어, `on_update` 안에서 총알 엔티티를 생성하면 현재 순회 중인 목록이 변하게 된다. 지연 처리로 이 문제를 안전하게 해결한다.

```python
class Shooter(engine.Component):
    def on_update(self, dt):
        if should_fire():
            bullet = engine.Entity("Bullet")
            bullet.position = self.position.copy()
            bullet.add_component(BulletMovement())
            bullet.add_component(BulletRenderer())
            # 이 시점에 world에 직접 추가해도 안전하다.
            # 실제 추가는 다음 update() 호출 시점에 이루어진다.
            self.entity._world.add(bullet)  # 대기열에만 추가됨
```

### World 메서드

```python
from engine import World, Entity

world = World()

# 추가 (지연)
entity = world.add(Entity("player"))

# 제거 (지연)
world.remove(entity)

# 업데이트 (추가/제거 처리 + on_start + on_update + on_late_update)
world.update(dt)

# 그리기 (on_draw 호출)
world.draw(renderer)

# 모든 엔티티 즉시 제거 (on_destroy 호출)
world.clear()

# 엔티티 수
print(len(world))
```

### 쿼리 메서드

World에서 특정 조건의 엔티티를 검색할 수 있다.

#### find_by_name

```python
player = world.find_by_name("Player")  # Entity | None
if player:
    print(player.position)
```

#### find_by_tag

```python
enemies = world.find_by_tag("enemy")  # list[Entity]
for enemy in enemies:
    print(f"{enemy.name}: {enemy.position}")
```

#### find_by_type

```python
# Entity 서브클래스 타입으로 검색 (서브클래스를 사용하는 경우)
custom_entities = world.find_by_type(CustomEntity)
```

#### find_with_component

특정 Component 타입을 **모두** 가진 엔티티를 검색한다. 이전의 `query()` 메서드를 대체한다.

```python
# Health와 PlayerMovement 컴포넌트를 모두 가진 엔티티
players = world.find_with_component(Health, PlayerMovement)
for entity in players:
    hp = entity.get_component(Health)
    if hp.is_alive:
        print(f"{entity.name}: HP={hp.hp}")
```

---

## World의 update/draw 상세 흐름

```
world.update(dt):
+-----------------------------------------------+
|  1. _process_additions() (대기 중인 추가)       |
|     for entity in _to_add:                     |
|         entity._world = self                   |
|         entities.append(entity)                |
|     _to_add.clear()                            |
|                                                |
|  2. _start_components() (새 컴포넌트 시작)      |
|     for entity in entities:                    |
|         if entity.active:                      |
|             for comp in components:            |
|                 if comp.enabled and not started:|
|                     comp.on_start()            |
|                     comp._started = True       |
|                                                |
|  3. _update_components(dt)                     |
|     for entity in entities:                    |
|         if entity.active:                      |
|             for comp in components:            |
|                 if comp.enabled:               |
|                     comp.on_update(dt)         |
|                                                |
|  4. _late_update_components(dt)                |
|     for entity in entities:                    |
|         if entity.active:                      |
|             for comp in components:            |
|                 if comp.enabled:               |
|                     comp.on_late_update(dt)    |
|                                                |
|  5. _process_removals() (대기 중인 제거)        |
|     for entity in _to_remove:                  |
|         entity._destroy_components()           |
|         entity._world = None                   |
|         entities.remove(entity)                |
|     _to_remove.clear()                         |
+-----------------------------------------------+

world.draw(renderer):
+-----------------------------------------------+
|  for entity in entities:                       |
|      if entity.active:                         |
|          for comp in components:               |
|              if comp.enabled:                  |
|                  comp.on_draw(renderer)        |
+-----------------------------------------------+
```

---

## 실전 예제

### Player (Entity + 여러 Component)

```python
import engine

# --- Components ---

class PlayerMovement(engine.Component):
    def on_start(self):
        self.speed = 200.0
        self.run_speed = 400.0

    def on_update(self, dt):
        kb = engine.current_app().keyboard
        direction = engine.Vector2.zero()
        if kb.is_pressed(engine.Key.W): direction = direction + engine.Vector2.up()
        if kb.is_pressed(engine.Key.S): direction = direction + engine.Vector2.down()
        if kb.is_pressed(engine.Key.A): direction = direction + engine.Vector2.left()
        if kb.is_pressed(engine.Key.D): direction = direction + engine.Vector2.right()

        speed = self.run_speed if kb.is_pressed(engine.Key.LSHIFT) else self.speed
        if direction.magnitude > 0:
            self.transform.translate(direction.normalized * speed * dt)


class PlayerRenderer(engine.Component):
    def on_awake(self):
        self.color = engine.Color.BLUE
        self.size = 32

    def on_draw(self, renderer):
        p = self.position
        half = self.size / 2
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size, self.color)

        # 체력바
        hp = self.entity.get_component(Health)
        if hp:
            bar_x = p.x - 20
            bar_y = p.y - half - 8
            renderer.draw_rect(bar_x, bar_y, 40, 4, engine.Color.RED, layer=1)
            renderer.draw_rect(bar_x, bar_y, 40 * hp.ratio, 4, engine.Color.GREEN, layer=1)


# --- Scene ---

class GameScene(engine.Scene):
    def on_enter(self):
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_tag("player")
        player.add_component(PlayerMovement())
        player.add_component(PlayerRenderer())
        player.add_component(Health())
        self.add(player)

    def on_exit(self):
        self.world.clear()
```

### AI 추적 컴포넌트

```python
class ChaseTarget(engine.Component):
    """태그로 대상을 찾아 추적하는 컴포넌트."""

    def on_start(self):
        self.speed = 80.0
        self.target_tag = "player"
        self.stop_distance = 30.0

    def on_update(self, dt):
        targets = self.entity._world.find_by_tag(self.target_tag)
        if not targets:
            return

        target = targets[0]
        to_target = target.position - self.position
        distance = to_target.magnitude

        if distance > self.stop_distance:
            direction = to_target.normalized
            self.transform.translate(direction * self.speed * dt)
            self.transform.look_at(target.position)


class EnemyRenderer(engine.Component):
    def on_awake(self):
        self.color = engine.Color.RED
        self.size = 24

    def on_draw(self, renderer):
        p = self.position
        half = self.size / 2
        renderer.draw_rect(p.x - half, p.y - half, self.size, self.size, self.color)

        hp = self.entity.get_component(Health)
        if hp:
            bar_x = p.x - 15
            bar_y = p.y - half - 6
            renderer.draw_rect(bar_x, bar_y, 30, 3, engine.Color.DARK_GRAY, layer=1)
            renderer.draw_rect(bar_x, bar_y, 30 * hp.ratio, 3, engine.Color.YELLOW, layer=1)
```

### Projectile (수명 제한 컴포넌트)

```python
class BulletMovement(engine.Component):
    def on_start(self):
        self.speed = 400.0
        self.lifetime = 3.0

    def on_update(self, dt):
        # 직선 이동 (forward 방향)
        direction = self.transform.forward
        self.transform.translate(direction * self.speed * dt)

        # 수명 감소
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.entity._world.remove(self.entity)
            return

        # 적과 충돌 검사
        enemies = self.entity._world.find_by_tag("enemy")
        for enemy in enemies:
            if self.position.distance_to(enemy.position) < 20:
                hp = enemy.get_component(Health)
                if hp:
                    hp.damage(25)
                    if not hp.is_alive:
                        self.entity._world.remove(enemy)
                self.entity._world.remove(self.entity)
                break


class BulletRenderer(engine.Component):
    def on_draw(self, renderer):
        p = self.position
        renderer.draw_rect(p.x - 3, p.y - 3, 6, 6, engine.Color.YELLOW)
```

### 모든 것을 연결: 전체 게임

```python
import engine
import random

class ShootOnClick(engine.Component):
    """마우스 클릭으로 총알을 발사하는 컴포넌트."""

    def on_update(self, dt):
        app = engine.current_app()
        if app.keyboard.is_just_pressed(engine.Key.SPACE):
            mouse_pos = app.mouse.position
            bullet = engine.Entity("Bullet")
            bullet.position = self.position.copy()
            bullet.transform.look_at(mouse_pos)
            bullet.add_component(BulletMovement())
            bullet.add_component(BulletRenderer())
            self.entity._world.add(bullet)


class QuitOnEscape(engine.Component):
    def on_update(self, dt):
        if engine.current_app().keyboard.is_just_pressed(engine.Key.ESCAPE):
            engine.current_app().quit()


class GameScene(engine.Scene):
    def on_enter(self):
        # 컨트롤러 (종료 처리)
        controller = engine.Entity("Controller")
        controller.add_component(QuitOnEscape())
        self.add(controller)

        # 플레이어
        player = engine.Entity("Player")
        player.position = engine.Vector2(400, 300)
        player.add_tag("player")
        player.add_component(PlayerMovement())
        player.add_component(PlayerRenderer())
        player.add_component(Health())
        player.add_component(ShootOnClick())
        self.add(player)

        # 적 여러 마리
        for i in range(5):
            enemy = engine.Entity(f"Enemy_{i}")
            enemy.position = engine.Vector2(
                random.randint(50, 750),
                random.randint(50, 550),
            )
            enemy.add_tag("enemy")
            enemy.add_component(ChaseTarget())
            enemy.add_component(EnemyRenderer())
            hp = enemy.add_component(Health())
            hp.hp = 50
            hp.max_hp = 50
            self.add(enemy)

    def on_exit(self):
        self.world.clear()


# --- Run ---

game = engine.Game(title="ECS Demo", width=800, height=600)
game.run(GameScene())
```

---

## 다음 단계

- [씬 관리](scene.md) -- World를 소유하는 Scene과 씬 전환 방법.
- [렌더링](rendering.md) -- on_draw에서 사용하는 Renderer API.
- [수학 모듈](math.md) -- Transform2D, Vector2의 상세 사용법.
