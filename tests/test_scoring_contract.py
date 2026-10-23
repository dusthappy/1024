"""Public scoring/plotting contracts; run with python3 -B -m unittest discover -s tests.

The score oracle uses integer arithmetic rather than the implementation's
Decimal formula. SVG checks inspect geometry and visible text properties;
font bounds are conservative estimates, not a replacement for rendered QA.
"""

from collections import Counter
from decimal import Decimal
from itertools import product
import math
from pathlib import Path
import sys
import unicodedata
import unittest
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'programmer-day-1024' / 'scripts'))
import render_radar
import score_profile

VERSION = '1024-8d-v3'
NS = {'s': 'http://www.w3.org/2000/svg'}
DIMENSIONS = ('创意构思', '目标表达', 'AI统筹', '判断取舍', '迭代打磨', '知识复用', '多元表达', '应变交付')


def rating_data(rating):
    return {'rubric_version': VERSION, 'ratings': {
        name: dict(zip(('A', 'B', 'C', 'E'), rating)) for name in DIMENSIONS
    }}


def score(rating):
    return score_profile.score_profile(rating_data(rating))['scores'][DIMENSIONS[0]]


def group(root, name):
    return root.find(f"s:g[@id='{name}']", NS)


def svg_point(axis, score_value):
    angle = -math.pi / 2 + axis * math.pi / 4
    return 600 + 30 * score_value * math.cos(angle), 500 + 30 * score_value * math.sin(angle)


def properties(node):
    values = dict(node.attrib)
    values.update(part.split(':', 1) for part in node.get('style', '').split(';') if ':' in part)
    return {key.strip(): value.strip() for key, value in values.items()}


def ancestor_chain(node, parents):
    chain = [node]
    while node in parents:
        node = parents[node]
        chain.append(node)
    return list(reversed(chain))


def effective_properties(node, parents):
    values = {}
    for ancestor in ancestor_chain(node, parents):
        values.update(properties(ancestor))
    return values


def numeric(value):
    return float(value.removesuffix('px'))


def rgb(hex_color):
    if len(hex_color) == 4:
        hex_color = '#' + ''.join(character * 2 for character in hex_color[1:])
    if len(hex_color) != 7 or not hex_color.startswith('#'):
        raise AssertionError(f'Unsupported SVG color in visibility check: {hex_color}')
    return tuple(int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5))


def luminance(color):
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in color]
    return sum(weight * value for weight, value in zip((0.2126, 0.7152, 0.0722), linear))


class ScoringContractTests(unittest.TestCase):
    def test_all_integer_ratings_match_independent_oracle_and_distribution(self):
        non_null = []
        null_count = 0
        for a, b, c, e in product(range(5), repeat=4):
            with self.subTest(rating=(a, b, c, e)):
                actual = score((a, b, c, e))
                if a + b == 0:
                    self.assertIsNone(actual)
                    null_count += 1
                else:
                    # Raw score N/8; round 10*N/8 half-up using integers only.
                    n = 5 * (a + b) + 4 * c + 6 * e
                    tenths = (5 * n + 2) // 4
                    self.assertEqual(Decimal(str(actual)), Decimal(tenths) / 10)
                    non_null.append(tenths)
        distinct = sorted(set(non_null))
        self.assertEqual((len(non_null), null_count, len(distinct)), (600, 25, 68))
        self.assertEqual(Counter(b - a for a, b in zip(distinct, distinct[1:])), {1: 47, 2: 17, 3: 1, 5: 2})
        self.assertEqual((distinct[0], distinct[-1]), (6, 100))
        self.assertNotIn(87, distinct)

    def test_half_up_and_missing_evidence_are_distinct(self):
        self.assertEqual(score((1, 1, 0, 0)), 1.3)  # 1.25 must not become 1.2.
        self.assertEqual(score((4, 4, 3, 3)), 8.8)  # 8.75 must become 8.8.
        self.assertEqual(score((4, 4, 4, 4)), 10.0)
        self.assertIsNone(score((0, 0, 4, 4)))
        payload = rating_data((1, 1, 0, 0))
        payload['ratings'][DIMENSIONS[0]] = None
        self.assertIsNone(score_profile.score_profile(payload)['scores'][DIMENSIONS[0]])

    def test_version_and_integer_ratings_are_strict(self):
        self.assertEqual(render_radar.RUBRIC_VERSION, VERSION)
        for version in ('1024-8d-v1', '1024-8d-v2', '1024-8d-v4', None):
            with self.subTest(version=version):
                payload = rating_data((3, 3, 3, 3))
                payload['rubric_version'] = version
                with self.assertRaises(ValueError):
                    score_profile.score_profile(payload)
                with self.assertRaises(ValueError):
                    render_radar.validate_data({'rubric_version': version, 'scores': dict.fromkeys(DIMENSIONS, 7.5)})
        for invalid in (True, False, 3.0, Decimal('3.0'), '3', -1, 5, None):
            with self.subTest(invalid=invalid):
                payload = rating_data((3, 3, 3, 3))
                payload['ratings'][DIMENSIONS[0]]['A'] = invalid
                with self.assertRaises(ValueError):
                    score_profile.score_profile(payload)

    def test_key_order_does_not_change_scores_or_svg(self):
        payload = rating_data((2, 3, 1, 4))
        expected = score_profile.score_profile(payload)
        payload['ratings'] = dict(reversed(list(payload['ratings'].items())))
        self.assertEqual(score_profile.score_profile(payload), expected)
        ordered = render_radar.validate_data(expected)
        expected['scores'] = dict(reversed(list(expected['scores'].items())))
        shuffled = render_radar.validate_data(expected)
        self.assertEqual(render_radar.render_svg(shuffled), render_radar.render_svg(ordered))

    def test_ten_point_geometry_and_fixed_axis_order(self):
        scores = (2.5, 7.3, 10.0, 8.0, 0.0, 5.0, 6.3, 9.4)
        root = ET.fromstring(render_radar.render_svg(scores))
        self.assertEqual([node[0].text for node in group(root, 'radar-labels')], list(DIMENSIONS))
        self.assertEqual([node[1].text for node in group(root, 'radar-labels')], [f'{value:.1f}' for value in scores])
        self.assertEqual([node.text for node in group(root, 'radar-scale')], ['2.0', '4.0', '6.0', '8.0', '10.0'])
        circles = group(root, 'radar-data').findall('s:circle', NS)
        self.assertEqual(len(circles), 8)
        self.assertEqual({int(circle.get('data-axis')) for circle in circles}, set(range(8)))
        for circle in circles:
            axis = int(circle.get('data-axis'))
            x, y = svg_point(axis, scores[axis])
            self.assertAlmostEqual(float(circle.get('cx')), x, places=5)
            self.assertAlmostEqual(float(circle.get('cy')), y, places=5)
        self.assertEqual(len(group(root, 'radar-data').findall('s:polygon', NS)), 1)

    def test_unknown_axes_are_not_zero_or_bridged(self):
        for scores, edges in (
            ((None,) * 8, set()),
            ((10, None, None, None, None, None, None, 2.5), {(7, 0)}),
            ((0, None, 7.3, None, None, None, None, None), set()),
            ((2.5, 7.3, None, None, None, None, None, None), {(0, 1)}),
        ):
            with self.subTest(scores=scores):
                root = ET.fromstring(render_radar.render_svg(scores))
                data = group(root, 'radar-data')
                lines = data.findall('s:line', NS)
                self.assertEqual({(int(node.get('data-from')), int(node.get('data-to'))) for node in lines}, edges)
                self.assertFalse(data.findall('s:polygon', NS))
                self.assertEqual(len(data.findall('s:circle', NS)), sum(value is not None for value in scores))
                self.assertEqual(len(group(root, 'radar-axes')), 8)
                self.assertEqual(sum(node[1].text == '待探索' for node in group(root, 'radar-labels')), scores.count(None))
                for line in lines:
                    for suffix, axis_key in (('1', 'data-from'), ('2', 'data-to')):
                        axis = int(line.get(axis_key))
                        x, y = svg_point(axis, scores[axis])
                        self.assertAlmostEqual(float(line.get('x' + suffix)), x, places=5)
                        self.assertAlmostEqual(float(line.get('y' + suffix)), y, places=5)

    def test_precision_qualifications_are_visibly_as_readable_as_axis_names(self):
        for theme in ('light', 'dark'):
            with self.subTest(theme=theme):
                root = ET.fromstring(render_radar.render_svg((7.5,) * 8, theme))
                parents = {child: parent for parent in root.iter() for child in parent}
                axis_size = max(numeric(effective_properties(node[0], parents)['font-size']) for node in group(root, 'radar-labels'))
                vx, vy, width, height = map(float, root.get('viewBox').split())
                background = rgb(root.find('s:rect', NS).get('fill'))
                visible_text = root.findall('.//s:text', NS)
                for marker in ('非专业测评', '分项等级加权展示', '小数不代表测量精度'):
                    matches = [node for node in visible_text if marker in ''.join(node.itertext())]
                    self.assertEqual(len(matches), 1, f'One visible qualification required: {marker}')
                    node = matches[0]
                    props = effective_properties(node, parents)
                    font_size = numeric(props['font-size'])
                    self.assertGreaterEqual(font_size, 24, marker)
                    self.assertGreaterEqual(font_size, axis_size, marker)
                    self.assertNotIn(props.get('visibility', 'visible'), ('hidden', 'collapse'))
                    alpha = float(props.get('fill-opacity', '1'))
                    for ancestor in ancestor_chain(node, parents):
                        ancestor_props = properties(ancestor)
                        self.assertNotEqual(ancestor_props.get('display'), 'none')
                        self.assertEqual(ancestor_props.get('clip-path', 'none'), 'none')
                        self.assertEqual(ancestor_props.get('mask', 'none'), 'none')
                        self.assertNotIn(ancestor.tag.rsplit('}', 1)[-1], ('defs', 'symbol', 'clipPath', 'mask'))
                        self.assertFalse(ancestor.get('transform'), 'Update bounds check if qualifications gain transforms')
                        alpha *= float(ancestor_props.get('opacity', '1'))
                    self.assertGreater(alpha, 0)
                    foreground = rgb(props.get('fill', '#000000'))
                    composite = tuple(alpha * fg + (1 - alpha) * bg for fg, bg in zip(foreground, background))
                    lights = sorted((luminance(composite), luminance(background)))
                    self.assertGreaterEqual((lights[1] + .05) / (lights[0] + .05), 4.5, marker)
                    text = ''.join(node.itertext())
                    estimated_width = sum(1 if unicodedata.east_asian_width(char) in ('W', 'F') else .7 for char in text) * font_size
                    x, y = numeric(node.get('x', '0')), numeric(node.get('y', '0'))
                    anchor = props.get('text-anchor', 'start')
                    left = x - (estimated_width / 2 if anchor == 'middle' else estimated_width if anchor == 'end' else 0)
                    self.assertGreaterEqual(left, vx)
                    self.assertLessEqual(left + estimated_width, vx + width)
                    self.assertGreaterEqual(y - font_size, vy)
                    self.assertLessEqual(y + .3 * font_size, vy + height)


if __name__ == '__main__':
    unittest.main()
