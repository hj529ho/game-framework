"""Tests for engine.ui module."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from engine.ui.core.units import px, pct, auto
from engine.ui.core.style import Style, EdgeInsets
from engine.ui.core.element import Element
from engine.ui.core.layout import compute_layout
from engine.ui.core.css_parser import parse_css, parse_color, parse_length, parse_edge_shorthand
from engine.ui.core.stylesheet import Stylesheet
from engine.ui.elements.div import Div
from engine.ui.elements.text import Text
from engine.ui.elements.button import Button
from engine.ui.elements.progress_bar import ProgressBar
from engine.ui.events import ClickEvent, HoverEvent
from engine.renderer.color import Color
from engine.math.vector2 import Vector2


# --- CSS Parser ---

def test_parse_css():
    result = parse_css("width: 200px; height: 50%; padding: 10px")
    assert result["width"] == "200px"
    assert result["height"] == "50%"
    assert result["padding"] == "10px"

def test_parse_length_px():
    val, unit = parse_length("100px")
    assert val == 100.0 and unit == "px"

def test_parse_length_percent():
    val, unit = parse_length("50%")
    assert val == 50.0 and unit == "%"

def test_parse_length_auto():
    val, unit = parse_length("auto")
    assert unit == "auto"

def test_parse_color_hex():
    c = parse_color("#ff0000")
    assert c == Color(255, 0, 0)

def test_parse_color_hex_short():
    c = parse_color("#f00")
    assert c == Color(255, 0, 0)

def test_parse_color_named():
    assert parse_color("red") == Color(255, 0, 0)
    assert parse_color("white") == Color(255, 255, 255)
    assert parse_color("transparent") == Color(0, 0, 0, 0)

def test_parse_color_rgb():
    c = parse_color("rgb(100, 200, 50)")
    assert c == Color(100, 200, 50)

def test_parse_color_rgba():
    c = parse_color("rgba(100, 200, 50, 0.5)")
    assert c.r == 100 and c.g == 200 and c.b == 50
    assert abs(c.a - 127) <= 1

def test_parse_edge_shorthand_1():
    assert parse_edge_shorthand("10px") == (10, 10, 10, 10)

def test_parse_edge_shorthand_2():
    assert parse_edge_shorthand("10px 20px") == (10, 20, 10, 20)

def test_parse_edge_shorthand_4():
    assert parse_edge_shorthand("10px 20px 30px 40px") == (10, 20, 30, 40)


# --- Style ---

def test_style_css_string():
    s = Style("width: 200px; height: 100px; padding: 10px; background: red")
    assert s.width == px(200)
    assert s.height == px(100)
    assert s.padding == EdgeInsets.all(10)
    assert s.background_color == Color(255, 0, 0)

def test_style_flex_direction():
    s = Style("display: flex; flex-direction: row; gap: 5px; justify-content: center")
    assert s.display == "flex"
    assert s.direction == "row"
    assert s.gap == 5.0
    assert s.justify_content == "center"

def test_style_border_shorthand():
    s = Style("border: 2px solid white")
    assert s.border_width == 2.0
    assert s.border_color == Color(255, 255, 255)

def test_style_inheritance():
    parent = Style("color: white; font-size: 14px")
    child = Style("font-size: 20px")
    child.resolve_inherited(parent)
    assert child.color == Color(255, 255, 255)  # inherited
    assert child.font_size == 20  # not overridden


# --- Stylesheet ---

def test_stylesheet_class():
    sheet = Stylesheet()
    sheet.add(".panel", "background: #333; padding: 10px")
    div = Div(class_name="panel")
    sheet.apply(div)
    assert div.style.background_color == Color(51, 51, 51)
    assert div.style.padding.top == 10

def test_stylesheet_id():
    sheet = Stylesheet()
    sheet.add("#score", "color: gold")
    el = Text("0", id="score")
    sheet.apply(el)
    assert el.style.color == Color(255, 215, 0)

def test_stylesheet_apply_tree():
    sheet = Stylesheet()
    sheet.add(".item", "padding: 5px")
    root = Div()
    c1 = Div(class_name="item")
    c2 = Div(class_name="item")
    root.append(c1)
    root.append(c2)
    sheet.apply_tree(root)
    assert c1.style.padding.top == 5
    assert c2.style.padding.top == 5


# --- Element tree ---

def test_element_append_remove():
    root = Element()
    child = Element()
    root.append(child)
    assert len(root.children) == 1
    assert child.parent is root
    root.remove(child)
    assert len(root.children) == 0
    assert child.parent is None

def test_element_find_by_id():
    root = Element()
    a = Element(id="a")
    b = Element(id="b")
    root.append(a)
    a.append(b)
    assert root.find_by_id("b") is b
    assert root.find_by_id("missing") is None

def test_element_event_bubbling():
    events = []
    root = Element()
    child = Element()
    root.append(child)
    child.on("click", lambda e: events.append("child"))
    root.on("click", lambda e: events.append("root"))
    child.emit("click", ClickEvent(x=0, y=0))
    assert events == ["child", "root"]

def test_element_stop_propagation():
    events = []
    root = Element()
    child = Element()
    root.append(child)

    def stop_handler(e):
        events.append("child")
        e.stop_propagation()

    child.on("click", stop_handler)
    root.on("click", lambda e: events.append("root"))
    child.emit("click", ClickEvent(x=0, y=0))
    assert events == ["child"]  # root not reached

def test_element_class_name():
    el = Div(class_name="panel dark")
    assert el.class_name == "panel dark"


# --- Layout ---

def test_layout_column():
    root = Div(style="width: 400px; flex-direction: column; gap: 10px")
    c1 = Div(style="width: 100px; height: 50px")
    c2 = Div(style="width: 100px; height: 50px")
    root.append(c1)
    root.append(c2)
    compute_layout(root, 800, 600)
    assert c1._computed_y == 0
    assert c2._computed_y == 60  # 50 + 10 gap

def test_layout_row():
    root = Div(style="width: 400px; height: 50px; flex-direction: row; gap: 10px")
    c1 = Div(style="width: 100px; height: 40px")
    c2 = Div(style="width: 100px; height: 40px")
    root.append(c1)
    root.append(c2)
    compute_layout(root, 800, 600)
    assert c1._computed_x == 0
    assert c2._computed_x == 110  # 100 + 10 gap

def test_layout_justify_space_between():
    root = Div(style="width: 400px; height: 50px; flex-direction: row; "
                     "justify-content: space-between")
    a = Div(style="width: 50px; height: 40px")
    b = Div(style="width: 50px; height: 40px")
    root.append(a)
    root.append(b)
    compute_layout(root, 800, 600)
    assert a._computed_x == 0
    assert b._computed_x == 350  # 400 - 50

def test_layout_flex_grow():
    root = Div(style="width: 300px; height: 50px; flex-direction: row")
    fixed = Div(style="width: 100px; height: 50px")
    grow = Div(style="height: 50px; flex-grow: 1")
    root.append(fixed)
    root.append(grow)
    compute_layout(root, 800, 600)
    assert grow._computed_w > 100  # should fill remaining space


# --- Elements ---

def test_div_style():
    d = Div(style="width: 200px; background: #ff0000")
    assert d.style.background_color == Color(255, 0, 0)

def test_text_content():
    t = Text("Hello")
    assert t.content == "Hello"
    t.content = "World"
    assert t.content == "World"

def test_button_label():
    b = Button("OK")
    assert b.label == "OK"
    b.label = "Cancel"
    assert b.label == "Cancel"

def test_progress_bar_value():
    bar = ProgressBar(0.75)
    assert bar.value == 0.75
    bar.value = 0.1
    assert bar.value == 0.1
    bar.value = 2.0  # clamped
    assert bar.value == 1.0
    bar.value = -1.0
    assert bar.value == 0.0

def test_progress_bar_auto_color():
    bar = ProgressBar(0.1)
    assert bar._get_fill_color() == Color.RED
    bar.value = 0.4
    assert bar._get_fill_color() == Color.YELLOW
    bar.value = 0.8
    assert bar._get_fill_color() == Color.GREEN


# --- Units ---

def test_px_resolve():
    assert px(100).resolve(500) == 100

def test_pct_resolve():
    assert pct(50).resolve(200) == 100

def test_auto_is_auto():
    assert auto.is_auto()
    assert not px(10).is_auto()

def test_edge_insets():
    e = EdgeInsets.all(10)
    assert e.horizontal == 20
    assert e.vertical == 20

    e2 = EdgeInsets.symmetric(vertical=5, horizontal=10)
    assert e2.top == 5 and e2.left == 10
