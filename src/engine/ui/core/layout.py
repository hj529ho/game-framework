"""Flexbox layout engine.

Computes _computed_x, _computed_y, _computed_w, _computed_h
on every Element in the tree.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from engine.ui.core.units import auto

if TYPE_CHECKING:
    from engine.ui.core.element import Element


def compute_layout(root: Element, available_w: float, available_h: float) -> None:
    """Compute layout for the entire element tree."""
    _resolve_size(root, available_w, available_h)
    root._computed_x = root.style.margin.left
    root._computed_y = root.style.margin.top
    _layout_children(root)


def _resolve_size(el: Element, parent_w: float, parent_h: float) -> None:
    """Resolve width/height from style units."""
    s = el.style

    # Width
    if s.width.is_auto():
        el._computed_w = parent_w - s.margin.horizontal
    else:
        el._computed_w = s.width.resolve(parent_w)

    # Height
    if s.height.is_auto():
        el._computed_h = 0  # will be expanded by content
    else:
        el._computed_h = s.height.resolve(parent_h)

    # Clamp
    el._computed_w = max(s.min_width, min(s.max_width, el._computed_w))
    el._computed_h = max(s.min_height, min(s.max_height, el._computed_h))


def _layout_children(parent: Element) -> None:
    """Layout children using flexbox."""
    s = parent.style
    children = [c for c in parent._children
                if c._visible and c.style.display != "none"]

    if not children:
        # Auto-height with no children: just padding + border
        if s.height.is_auto():
            parent._computed_h = s.padding.vertical + s.border_width * 2
        return

    content_w = parent._computed_w - s.padding.horizontal - s.border_width * 2
    content_h = parent._computed_h - s.padding.vertical - s.border_width * 2

    # Handle absolute-positioned children separately
    flow_children = []
    for child in children:
        if child.style.position == "absolute":
            _layout_absolute(child, parent)
        else:
            flow_children.append(child)

    if not flow_children:
        if s.height.is_auto():
            parent._computed_h = s.padding.vertical + s.border_width * 2
        return

    is_row = (s.direction == "row")
    main_size = content_w if is_row else content_h
    cross_size = content_h if is_row else content_w

    # 1. Resolve child sizes
    for child in flow_children:
        child_parent_w = content_w
        child_parent_h = content_h if content_h > 0 else 10000
        _resolve_size(child, child_parent_w, child_parent_h)

    # 2. Calculate total main-axis size
    total_main = 0.0
    for child in flow_children:
        cm = child.style.margin
        if is_row:
            total_main += child._computed_w + cm.horizontal
        else:
            total_main += child._computed_h + cm.vertical

    total_gaps = s.gap * max(0, len(flow_children) - 1)
    total_main += total_gaps

    # 3. Flex grow/shrink (only if parent has a definite size on main axis)
    parent_main_auto = (not is_row and s.height.is_auto()) or (is_row and s.width.is_auto())
    remaining = main_size - total_main
    if remaining > 0 and not parent_main_auto:
        total_grow = sum(c.style.flex_grow for c in flow_children)
        if total_grow > 0:
            for child in flow_children:
                if child.style.flex_grow > 0:
                    extra = remaining * (child.style.flex_grow / total_grow)
                    if is_row:
                        child._computed_w += extra
                    else:
                        child._computed_h += extra
    elif remaining < 0 and not parent_main_auto:
        total_shrink = sum(c.style.flex_shrink for c in flow_children)
        if total_shrink > 0:
            for child in flow_children:
                if child.style.flex_shrink > 0:
                    shrink = (-remaining) * (child.style.flex_shrink / total_shrink)
                    if is_row:
                        child._computed_w = max(child.style.min_width, child._computed_w - shrink)
                    else:
                        child._computed_h = max(child.style.min_height, child._computed_h - shrink)

    # 4. Recalculate total main after flex
    total_main = 0.0
    for child in flow_children:
        cm = child.style.margin
        if is_row:
            total_main += child._computed_w + cm.horizontal
        else:
            total_main += child._computed_h + cm.vertical
    total_main += total_gaps

    # 5. Justify content (main axis offset and spacing)
    free_space = main_size - total_main
    main_offset, extra_gap = _justify(s.justify_content, free_space, len(flow_children))

    # 6. Position children
    cursor = main_offset
    for child in flow_children:
        cm = child.style.margin

        # Main axis position
        if is_row:
            child._computed_x = cursor + cm.left
            cursor += child._computed_w + cm.horizontal + s.gap
        else:
            child._computed_y = cursor + cm.top
            cursor += child._computed_h + cm.vertical + s.gap

        cursor += extra_gap

        # Cross axis alignment
        _align_cross(child, cross_size, is_row, s.align_items)

    # 7. Auto-height: expand parent to fit content
    if s.height.is_auto():
        if is_row:
            max_child_h = 0.0
            for child in flow_children:
                ch = child._computed_y + child._computed_h + child.style.margin.bottom
                max_child_h = max(max_child_h, ch)
            parent._computed_h = max_child_h + s.padding.vertical + s.border_width * 2
        else:
            parent._computed_h = cursor - s.gap + s.padding.vertical + s.border_width * 2

    # 8. Recursively layout grandchildren
    for child in flow_children:
        _layout_children(child)


def _layout_absolute(child: Element, parent: Element) -> None:
    """Position an absolutely-positioned child relative to parent content area."""
    s = child.style
    pw = parent._computed_w - parent.style.padding.horizontal - parent.style.border_width * 2
    ph = parent._computed_h - parent.style.padding.vertical - parent.style.border_width * 2

    _resolve_size(child, pw, ph)

    # Position from edges
    if s.left is not None:
        child._computed_x = s.left
    elif s.right is not None:
        child._computed_x = pw - child._computed_w - s.right
    else:
        child._computed_x = 0

    if s.top is not None:
        child._computed_y = s.top
    elif s.bottom is not None:
        child._computed_y = ph - child._computed_h - s.bottom
    else:
        child._computed_y = 0

    _layout_children(child)


def _justify(mode: str, free_space: float, count: int) -> tuple[float, float]:
    """Returns (initial_offset, extra_gap_between_items)."""
    if free_space < 0:
        free_space = 0

    if mode == "start":
        return 0, 0
    elif mode == "end":
        return free_space, 0
    elif mode == "center":
        return free_space / 2, 0
    elif mode == "space-between":
        if count <= 1:
            return 0, 0
        return 0, free_space / (count - 1)
    elif mode == "space-around":
        if count == 0:
            return 0, 0
        gap = free_space / count
        return gap / 2, gap - gap / count if count > 1 else 0
    elif mode == "space-evenly":
        if count == 0:
            return 0, 0
        gap = free_space / (count + 1)
        return gap, gap
    return 0, 0


def _align_cross(child: Element, cross_size: float, is_row: bool, align: str) -> None:
    """Align a child on the cross axis."""
    cm = child.style.margin

    if is_row:
        child_cross = child._computed_h
        if align == "start":
            child._computed_y = cm.top
        elif align == "end":
            child._computed_y = cross_size - child_cross - cm.bottom
        elif align == "center":
            child._computed_y = (cross_size - child_cross) / 2
        elif align == "stretch":
            child._computed_y = cm.top
            child._computed_h = cross_size - cm.vertical
    else:
        child_cross = child._computed_w
        if align == "start":
            child._computed_x = cm.left
        elif align == "end":
            child._computed_x = cross_size - child_cross - cm.right
        elif align == "center":
            child._computed_x = (cross_size - child_cross) / 2
        elif align == "stretch":
            child._computed_x = cm.left
            child._computed_w = cross_size - cm.horizontal
