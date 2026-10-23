#!/usr/bin/env python3
"""Render the fixed 1024 eight-dimension rubric as a standalone SVG.

Only Python's standard library is required. Unknown scores remain absent from
the data geometry; they are never treated as zero or interpolated across.
"""

from __future__ import annotations

import argparse
from decimal import Decimal
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


RUBRIC_VERSION = "1024-8d-v2"
DIMENSIONS = (
    "创意构思",
    "目标表达",
    "AI统筹",
    "判断取舍",
    "迭代打磨",
    "知识复用",
    "多元表达",
    "应变交付",
)
MAX_SCORE = 10
GRID_LEVELS = (2, 4, 6, 8, 10)
WIDTH, HEIGHT = 1200, 1000
CENTER_X, CENTER_Y, MAX_RADIUS = 600, 500, 300
LABEL_RADIUS = 365
SVG_NS = "http://www.w3.org/2000/svg"
FONT_FAMILY = (
    '"Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei", '
    '"Source Han Sans SC", system-ui, sans-serif'
)
THEMES = {
    "light": {
        "background": "#F7F9FC",
        "border": "#E1E7EF",
        "text": "#172A3A",
        "muted": "#617386",
        "grid": "#D5DFE9",
        "axis": "#C4D1DD",
        "accent": "#087F8C",
        "fill": "#14A6A1",
        "point_border": "#F7F9FC",
    },
    "dark": {
        "background": "#101A2A",
        "border": "#29394E",
        "text": "#EDF4FA",
        "muted": "#A6B6C8",
        "grid": "#2D4058",
        "axis": "#3A506A",
        "accent": "#5EEAD4",
        "fill": "#37C6AB",
        "point_border": "#101A2A",
    },
}


class RadarInputError(ValueError):
    """The input does not conform to the fixed rubric."""


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject duplicate JSON properties instead of silently keeping the last."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise RadarInputError(f"JSON 中存在重复键：{key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise RadarInputError(f"JSON 不允许非有限数值：{value}")


def validate_data(data: object) -> tuple[float | None, ...]:
    """Validate the complete schema and return scores in canonical axis order."""
    if not isinstance(data, dict):
        raise RadarInputError("输入顶层必须是 JSON 对象")
    if set(data) != {"rubric_version", "scores"}:
        raise RadarInputError("顶层必须且只能包含 rubric_version 和 scores")
    if data["rubric_version"] != RUBRIC_VERSION:
        raise RadarInputError(f"rubric_version 必须是 {RUBRIC_VERSION}")
    scores = data["scores"]
    if not isinstance(scores, dict):
        raise RadarInputError("scores 必须是包含完整八维键名的对象")
    missing = [name for name in DIMENSIONS if name not in scores]
    extra = sorted(set(scores) - set(DIMENSIONS))
    if missing or extra:
        details = []
        if missing:
            details.append("缺少：" + "、".join(missing))
        if extra:
            details.append("未知：" + "、".join(extra))
        raise RadarInputError("scores 的八维键名不匹配（" + "；".join(details) + "）")
    ordered = []
    for name in DIMENSIONS:
        value = scores[name]
        if value is None:
            ordered.append(None)
            continue
        if type(value) not in (int, float, Decimal):
            raise RadarInputError(f"{name} 只能是 null 或 0.0–10.0 的数值，最多一位小数")
        decimal_value = Decimal(str(value))
        if (
            not decimal_value.is_finite()
            or not 0 <= decimal_value <= MAX_SCORE
        ):
            raise RadarInputError(f"{name} 只能是 null 或 0.0–10.0 的数值，最多一位小数")
        parts = decimal_value.as_tuple()
        # Trailing zeros (7.30) are harmless; inspect digits without rounding.
        if parts.exponent < -1 and any(parts.digits[parts.exponent + 1:]):
            raise RadarInputError(f"{name} 只能是 null 或 0.0–10.0 的数值，最多一位小数")
        # Normalize integers and signed zero for deterministic one-decimal output.
        ordered.append(0.0 if decimal_value == 0 else float(decimal_value))
    return tuple(ordered)


def score_label(value: int | float | None) -> str:
    return "待探索" if value is None else f"{value:.1f}"


def point(axis: int, radius: float) -> tuple[float, float]:
    """Start at twelve o'clock and move clockwise in 45-degree increments."""
    angle = axis * math.tau / len(DIMENSIONS)
    return CENTER_X + math.sin(angle) * radius, CENTER_Y - math.cos(angle) * radius


def number(value: float) -> str:
    """Stable compact coordinates without insignificant negative zero."""
    formatted = f"{value:.6f}".rstrip("0").rstrip(".")
    return "0" if formatted == "-0" else formatted


def points_attribute(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{number(x)},{number(y)}" for x, y in points)


def element(parent: ET.Element, tag: str, **attrs: object) -> ET.Element:
    return ET.SubElement(
        parent,
        f"{{{SVG_NS}}}{tag}",
        {key.replace("_", "-"): str(value) for key, value in attrs.items()},
    )


def text_element(parent: ET.Element, content: str, **attrs: object) -> ET.Element:
    node = element(parent, "text", **attrs)
    node.text = content
    return node


def render_svg(scores: tuple[int | float | Decimal | None, ...], theme: str = "light") -> str:
    """Build deterministic SVG with no scripts, remote assets, or timestamps."""
    if theme not in THEMES:
        raise RadarInputError("theme 必须是 light 或 dark")
    if len(scores) != len(DIMENSIONS):
        raise RadarInputError("绘图需要完整的八维分数")
    # Keep the callable helper as strict as the command-line entry point.
    scores = validate_data({
        "rubric_version": RUBRIC_VERSION,
        "scores": dict(zip(DIMENSIONS, scores)),
    })
    palette = THEMES[theme]
    ET.register_namespace("", SVG_NS)
    root = ET.Element(f"{{{SVG_NS}}}svg", {
        "width": str(WIDTH),
        "height": str(HEIGHT),
        "viewBox": f"0 0 {WIDTH} {HEIGHT}",
        "role": "img",
        "aria-labelledby": "radar-title radar-description",
        "data-rubric-version": RUBRIC_VERSION,
        "data-theme": theme,
        "style": f"font-family: {FONT_FAMILY};",
    })
    element(root, "title", id="radar-title").text = "AI 创作高光图谱"
    element(root, "desc", id="radar-description").text = (
        "满分 10.0，活动趣味评分，非专业测评。按顶部顺时针顺序："
        + "；".join(
            f"{name}：{score_label(value)}"
            for name, value in zip(DIMENSIONS, scores)
        )
        + "。待探索维度没有数据点，也不参与连线或填充。"
    )
    element(root, "metadata").text = json.dumps(
        {"rubric_version": RUBRIC_VERSION, "scores": dict(zip(DIMENSIONS, scores))},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    element(root, "rect", x="1", y="1", width=WIDTH - 2, height=HEIGHT - 2,
            rx="28", fill=palette["background"], stroke=palette["border"])
    text_element(root, "AI 创作高光图谱", x="600", y="65", text_anchor="middle",
                 font_size="34", font_weight="700", fill=palette["text"])
    element(root, "line", x1="570", y1="86", x2="630", y2="86",
            stroke=palette["accent"], stroke_width="3", stroke_linecap="round")

    grid = element(root, "g", id="radar-grid", fill="none")
    for level in GRID_LEVELS:
        vertices = [point(axis, MAX_RADIUS * level / MAX_SCORE) for axis in range(8)]
        element(grid, "polygon", points=points_attribute(vertices),
                data_level=score_label(level), stroke=palette["grid"],
                stroke_width="1.6" if level == MAX_SCORE else "1")

    axes = element(root, "g", id="radar-axes", stroke=palette["axis"], stroke_width="1")
    for axis, name in enumerate(DIMENSIONS):
        x, y = point(axis, MAX_RADIUS)
        element(axes, "line", x1=CENTER_X, y1=CENTER_Y, x2=number(x), y2=number(y),
                data_axis=axis, data_dimension=name)

    scale = element(root, "g", id="radar-scale", fill=palette["muted"], font_size="13")
    for level in GRID_LEVELS:
        text_element(scale, score_label(level), x="610",
                     y=number(CENTER_Y - MAX_RADIUS * level / MAX_SCORE + 5))

    complete = all(value is not None for value in scores)
    data = element(root, "g", id="radar-data", data_complete=str(complete).lower())
    vertices = [
        None if value is None else point(axis, MAX_RADIUS * value / MAX_SCORE)
        for axis, value in enumerate(scores)
    ]
    if complete:
        element(data, "polygon", points=points_attribute([p for p in vertices if p is not None]),
                data_kind="area", fill=palette["fill"], fill_opacity="0.20",
                stroke=palette["accent"], stroke_width="3.5", stroke_linejoin="round")
    else:
        # Include the 7 -> 0 edge, but never bridge an unknown axis.
        for axis in range(len(DIMENSIONS)):
            next_axis = (axis + 1) % len(DIMENSIONS)
            start, end = vertices[axis], vertices[next_axis]
            if start is not None and end is not None:
                element(data, "line", x1=number(start[0]), y1=number(start[1]),
                        x2=number(end[0]), y2=number(end[1]),
                        data_from=axis, data_to=next_axis,
                        stroke=palette["accent"], stroke_width="3.5", stroke_linecap="round")
    for axis, vertex in enumerate(vertices):
        if vertex is not None:
            element(data, "circle", cx=number(vertex[0]), cy=number(vertex[1]), r="6",
                    data_axis=axis, data_score=scores[axis], fill=palette["accent"],
                    stroke=palette["point_border"], stroke_width="2.5")

    labels = element(root, "g", id="radar-labels")
    for axis, (name, value) in enumerate(zip(DIMENSIONS, scores)):
        x, y = point(axis, LABEL_RADIUS)
        anchor = "middle" if axis in (0, 4) else "start" if axis < 4 else "end"
        label = element(labels, "g", data_axis=axis, data_score="null" if value is None else value)
        text_element(label, name, x=number(x), y=number(y - 4), text_anchor=anchor,
                     font_size="24", font_weight="600", fill=palette["text"])
        text_element(label, score_label(value),
                     x=number(x), y=number(y + 27), text_anchor=anchor,
                     font_size="21" if value is None else "25", font_weight="650",
                     fill=palette["muted"] if value is None else palette["accent"])

    text_element(root, "满分 10.0 · 活动趣味评分 · 非专业测评", x="600", y="963", text_anchor="middle",
                 font_size="18", fill=palette["muted"])
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="输入评分 JSON 文件")
    parser.add_argument("--output", type=Path, required=True, help="输出独立 SVG 文件")
    parser.add_argument("--theme", choices=tuple(THEMES), default="light", help="配色，默认 light")
    parser.add_argument("--force", action="store_true", help="允许覆盖已有输出文件")
    args = parser.parse_args(argv)
    try:
        raw_data = json.loads(args.input.read_text(encoding="utf-8"),
                              object_pairs_hook=unique_object, parse_constant=reject_constant,
                              parse_float=Decimal)
        svg = render_svg(validate_data(raw_data), args.theme)
        # Exclusive creation is intentional: exists() followed by write() races.
        with args.output.open("w" if args.force else "x", encoding="utf-8", newline="\n") as stream:
            stream.write(svg)
    except FileExistsError:
        print(f"错误：输出已存在：{args.output}；如需覆盖请使用 --force", file=sys.stderr)
        return 2
    except (OSError, ValueError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 2
    print(f"已生成 SVG：{args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
