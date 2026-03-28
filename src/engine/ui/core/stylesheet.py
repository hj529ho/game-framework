"""Stylesheet: reusable named styles, like CSS classes.

Example:
    sheet = Stylesheet()
    sheet.add(".panel", "background: rgba(0,0,0,0.8); padding: 10px; border-radius: 8px")
    sheet.add(".title", "font-size: 24px; color: white; text-align: center")
    sheet.add(".hp-bar", "width: 200px; height: 20px; background: #333; border-radius: 4px")
    sheet.add("#score", "font-size: 18px; color: gold")

    # Apply to elements
    panel = Div(class_name="panel")
    sheet.apply(panel)

    # Or apply to entire tree
    sheet.apply_tree(root)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from engine.ui.core.style import Style

if TYPE_CHECKING:
    from engine.ui.core.element import Element


class Stylesheet:
    """Collection of named CSS rules."""

    def __init__(self) -> None:
        self._rules: dict[str, str] = {}  # selector -> CSS string

    def add(self, selector: str, css: str) -> Stylesheet:
        """Add a CSS rule. Supports .class and #id selectors."""
        self._rules[selector] = css
        return self

    def remove(self, selector: str) -> None:
        self._rules.pop(selector, None)

    def get(self, selector: str) -> str | None:
        return self._rules.get(selector)

    def apply(self, element: Element) -> None:
        """Apply matching rules to a single element's style."""
        # Apply class rules
        if element.class_name:
            for cls in element.class_name.split():
                css = self._rules.get(f".{cls}")
                if css:
                    element.style._apply_css(css)

        # Apply id rule
        if element.id:
            css = self._rules.get(f"#{element.id}")
            if css:
                element.style._apply_css(css)

    def apply_tree(self, root: Element) -> None:
        """Apply matching rules to an entire element tree (depth-first)."""
        self.apply(root)
        for child in root._children:
            self.apply_tree(child)

    def __repr__(self) -> str:
        return f"Stylesheet({len(self._rules)} rules)"
