#!/usr/bin/env python3
"""Calculate fixed 1024 eight-dimension scores from explicit evidence ratings.

Only Python's standard library is required. Ratings describe visible evidence,
not objective proficiency. Dimensions without direct A/B evidence remain null.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import sys

from render_radar import DIMENSIONS, RUBRIC_VERSION, reject_constant, unique_object


RATING_KEYS = ("A", "B", "C", "E")


class ProfileInputError(ValueError):
    """The input does not conform to the fixed evidence-rating schema."""


def validate_ratings(data: object) -> tuple[dict[str, int] | None, ...]:
    """Validate every dimension before calculating scores in canonical order."""
    if not isinstance(data, dict):
        raise ProfileInputError("输入顶层必须是 JSON 对象")
    if set(data) != {"rubric_version", "ratings"}:
        raise ProfileInputError("顶层必须且只能包含 rubric_version 和 ratings")
    if data["rubric_version"] != RUBRIC_VERSION:
        raise ProfileInputError(f"rubric_version 必须是 {RUBRIC_VERSION}")
    ratings = data["ratings"]
    if not isinstance(ratings, dict):
        raise ProfileInputError("ratings 必须是包含完整八维键名的对象")
    missing = [name for name in DIMENSIONS if name not in ratings]
    extra = sorted(set(ratings) - set(DIMENSIONS))
    if missing or extra:
        details = []
        if missing:
            details.append("缺少：" + "、".join(missing))
        if extra:
            details.append("未知：" + "、".join(extra))
        raise ProfileInputError("ratings 的八维键名不匹配（" + "；".join(details) + "）")

    ordered = []
    for name in DIMENSIONS:
        value = ratings[name]
        if value is None:
            ordered.append(None)
            continue
        if not isinstance(value, dict) or set(value) != set(RATING_KEYS):
            raise ProfileInputError(f"{name} 必须是 null 或恰好包含 A、B、C、E 的对象")
        for key in RATING_KEYS:
            rating = value[key]
            # bool, 3.0, strings, and partial/null ratings are not integer levels.
            if type(rating) is not int or not 0 <= rating <= 4:
                raise ProfileInputError(f"{name}.{key} 必须是 0–4 的整数")
        ordered.append({key: value[key] for key in RATING_KEYS})
    return tuple(ordered)


def score_profile(data: object) -> dict[str, object]:
    """Return only the renderer schema, with Decimal half-up calculation."""
    scores: dict[str, float | None] = {}
    for name, ratings in zip(DIMENSIONS, validate_ratings(data)):
        if ratings is None or ratings["A"] + ratings["B"] == 0:
            scores[name] = None
            continue
        score = (
            Decimal("0.625") * (ratings["A"] + ratings["B"])
            + Decimal("0.5") * ratings["C"]
            + Decimal("0.75") * ratings["E"]
        ).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        # json.dumps preserves the one-decimal representation, including 10.0.
        scores[name] = float(score)
    return {"rubric_version": RUBRIC_VERSION, "scores": scores}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="输入八维证据等级 JSON 文件")
    parser.add_argument("--output", type=Path, required=True, help="输出图表分数 JSON 文件")
    parser.add_argument("--force", action="store_true", help="允许覆盖已有输出文件")
    args = parser.parse_args(argv)
    try:
        # Resolve aliases and reject hard links as well, even when --force is set.
        if args.input.resolve() == args.output.resolve() or (
            args.output.exists() and args.input.samefile(args.output)
        ):
            raise ProfileInputError("输入与输出必须是不同文件")
        raw_data = json.loads(
            args.input.read_text(encoding="utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
            parse_float=Decimal,
        )
        result = score_profile(raw_data)
        payload = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        # Exclusive creation prevents silently replacing an existing artifact.
        with args.output.open("w" if args.force else "x", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
    except FileExistsError:
        print(f"错误：输出已存在：{args.output}；如需覆盖请使用 --force", file=sys.stderr)
        return 2
    except (OSError, ValueError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 2
    print(f"已生成评分 JSON：{args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
