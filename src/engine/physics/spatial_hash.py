from __future__ import annotations

from collections import defaultdict

from engine.math.rect import Rect
from engine.physics.collider import Collider


class SpatialHash:
    """Spatial hash grid for broadphase collision detection.

    Divides the world into a grid of cells. Each collider is inserted
    into all cells its AABB overlaps. Candidate pairs are found by
    querying colliders in the same cells.
    """

    def __init__(self, cell_size: float = 64.0) -> None:
        self._cell_size = cell_size
        self._cells: dict[tuple[int, int], list[Collider]] = defaultdict(list)

    @property
    def cell_size(self) -> float:
        return self._cell_size

    def clear(self) -> None:
        self._cells.clear()

    def insert(self, collider: Collider) -> None:
        bounds = collider.get_bounds()
        for cell in self._get_cells(bounds):
            self._cells[cell].append(collider)

    def query(self, collider: Collider) -> list[Collider]:
        """Return all other colliders sharing cells with this one."""
        bounds = collider.get_bounds()
        found: set[int] = set()
        result: list[Collider] = []
        for cell in self._get_cells(bounds):
            for other in self._cells[cell]:
                if other is not collider and id(other) not in found:
                    found.add(id(other))
                    result.append(other)
        return result

    def get_candidate_pairs(self) -> list[tuple[Collider, Collider]]:
        """Return all unique pairs of colliders sharing at least one cell."""
        seen: set[tuple[int, int]] = set()
        pairs: list[tuple[Collider, Collider]] = []

        for cell_colliders in self._cells.values():
            for i in range(len(cell_colliders)):
                for j in range(i + 1, len(cell_colliders)):
                    a = cell_colliders[i]
                    b = cell_colliders[j]
                    key = (min(id(a), id(b)), max(id(a), id(b)))
                    if key not in seen:
                        seen.add(key)
                        pairs.append((a, b))

        return pairs

    def _get_cells(self, bounds: Rect) -> list[tuple[int, int]]:
        cs = self._cell_size
        min_x = int(bounds.left // cs)
        max_x = int(bounds.right // cs)
        min_y = int(bounds.top // cs)
        max_y = int(bounds.bottom // cs)

        cells = []
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                cells.append((x, y))
        return cells
