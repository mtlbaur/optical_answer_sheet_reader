import cv2 as cv
import math

from oasr.utility import get_black_to_gray_image, div_color, mult_color, sort_by

contour_thickness = 2
circle_thickness = 2
rectangle_thickness = 2
ray_thickness = 2
text_thickness = 1


class Mark:
    def __init__(self, contour):
        self.contour = contour
        self.contour_area = cv.contourArea(contour)

        (self.x, self.y), self.radius = cv.minEnclosingCircle(contour)

        self.l = self.x - self.radius
        self.r = self.x + self.radius
        self.t = self.y - self.radius
        self.b = self.y + self.radius

    def __str__(self):
        return str(self.x) + ":" + str(self.y) + ":" + str(self.radius)


def get_center(m):
    return (m.x, m.y)


def get_int_center(m):
    return (int(m.x), int(m.y))


def draw_contour(m, image, color=(255, 255, 255), *args, **kwargs):
    cv.drawContours(image, [m.contour], 0, color, *args, **kwargs)


def draw_min_circle(m, image, color=(255, 255, 255), *args, **kwargs):
    cv.circle(image, (int(m.x), int(m.y)), int(m.radius), color, *args, **kwargs)


def draw_text(m, image, text, color=(255, 255, 255), *args, **kwargs):
    cv.putText(image, text, get_int_center(m), cv.FONT_HERSHEY_DUPLEX, 1, color, lineType=cv.LINE_AA, *args, **kwargs)


def draw_side_rays(m, image, sides, color=(255, 255, 255), *args, **kwargs):
    x, y, r = m.x, m.y, m.radius

    m = max(image.shape[0], image.shape[1])

    def to_int_tuple(t):
        return tuple(int(x) for x in t)

    def add_line(lines, start, end):
        lines.append((to_int_tuple(start), to_int_tuple(end)))

    lines = []

    if sides.find("t") != -1:
        add_line(lines, (x - r, y), (x - r, y - m))
        add_line(lines, (x + r, y), (x + r, y - m))

    if sides.find("b") != -1:
        add_line(lines, (x - r, y), (x - r, y + m))
        add_line(lines, (x + r, y), (x + r, y + m))

    if sides.find("l") != -1:
        add_line(lines, (x, y - r), (x - m, y - r))
        add_line(lines, (x, y + r), (x - m, y + r))

    if sides.find("r") != -1:
        add_line(lines, (x, y - r), (x + m, y - r))
        add_line(lines, (x, y + r), (x + m, y + r))

    for start, end in lines:
        cv.line(image, start, end, color, *args, **kwargs)


def is_close(a, b, attr_name, **kwargs):
    return math.isclose(getattr(a, attr_name), getattr(b, attr_name), **kwargs)


def are_close(a, b, args):
    return all(is_close(a, b, attr_name, **kwargs) for attr_name, kwargs in args)


def overlaps_with(a, b):
    return pow(a.x - b.x, 2) + pow(a.y - b.y, 2) <= pow(a.radius + b.radius, 2)


def aligns_with(a, b, attr_name):
    radius = min(a.radius, b.radius)

    return abs(getattr(a, attr_name) - getattr(b, attr_name)) <= radius


def find_marks(image, min_contour_area, max_contour_area, darkness_threshold):
    image = get_black_to_gray_image(image, upper=(darkness_threshold, darkness_threshold, darkness_threshold))

    marks = []

    contours, hierarchy = cv.findContours(image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    for con in contours:
        if (area := cv.contourArea(con)) >= min_contour_area and area <= max_contour_area:
            marks.append(Mark(con))

    return marks


def find_matching_edge_marks(marks: list[Mark], side, count, area_property, pos_rel_tol, area_rel_tol):
    groups = {
        "t": {
            "initial_sort": ["y", {}],
            "is_close": "y",
            "final_sort": "x",
        },
        "b": {
            "initial_sort": ["y", {"reverse": True}],
            "is_close": "y",
            "final_sort": "x",
        },
        "l": {
            "initial_sort": ["x", {}],
            "is_close": "x",
            "final_sort": "y",
        },
        "r": {
            "initial_sort": ["x", {"reverse": True}],
            "is_close": "x",
            "final_sort": "y",
        },
    }

    initial_sort, is_close, final_sort = groups[side].values()

    marks = sort_by(marks, *initial_sort[0], **initial_sort[1])

    group = []

    for a in marks:
        group = [a]

        for b in marks:
            if b is not a:
                if are_close(
                    a,
                    b,
                    [
                        [is_close, {"rel_tol": pos_rel_tol}],
                        [area_property, {"rel_tol": area_rel_tol}],
                    ],
                ):
                    group.append(b)

                    if len(group) == count:
                        return sort_by(group, final_sort)

    return group


def find_fill_marks(marks: list[Mark], lmarks: list[Mark], bmarks: list[Mark]):
    def in_bounds(x, y, l, r, t, b):
        return x >= l and x <= r and y >= t and y <= b

    def in_fill(x, y):
        return in_bounds(x, y, bmarks[0].l, bmarks[42].r, lmarks[0].t, lmarks[45].b)

    def in_exclusion(x, y):
        return in_bounds(x, y, bmarks[33].l, bmarks[42].r, lmarks[10].t, lmarks[13].b)

    fmarks = []

    for m in marks:
        if m not in bmarks and m not in lmarks:
            if any(in_fill(*p[0]) for p in m.contour) and not any(in_exclusion(*p[0]) for p in m.contour):
                fmarks.append(m)

    # filter out overlapping marks

    valid = set()

    for a in fmarks:
        if a not in valid:
            group = [a]

            for b in fmarks:
                if a is not b and b not in valid and overlaps_with(a, b):
                    group.append(b)

        valid.add(sort_by(group, "contour_area")[-1])

    return list(valid)


def draw_contours(image, marks, color=lambda: (255, 255, 255)):
    for m in marks:
        draw_contour(m, image, color(), contour_thickness)

    for m in marks:
        draw_text(m, image, f"{int(m.x)}:{int(m.y)}:{int(m.contour_area)}", (255, 255, 255), text_thickness)


def draw_edge_mark_circles(image, marks, color):
    for m in marks:
        draw_min_circle(m, image, color, circle_thickness)


def draw_edge_mark_rays(image, marks, sides, color):
    for m in marks:
        draw_side_rays(m, image, sides, color, ray_thickness)


def draw_edge_mark_indexes(image, marks):
    for i, m in enumerate(marks):
        draw_text(m, image, str(i), (255, 255, 255), text_thickness)


def draw_edge_marks(image, marks, sides, color):
    dark_color = mult_color(color, 1 / 3)

    for m in marks:
        draw_min_circle(m, image, color, circle_thickness)
        draw_side_rays(m, image, sides, dark_color, ray_thickness)

    for i, m in enumerate(marks):
        draw_text(m, image, str(i), (255, 255, 255), text_thickness)


def draw_fill_mark(image, mark, text, color=(255, 255, 255)):
    draw_min_circle(mark, image, div_color(color, 3), circle_thickness)
    draw_text(mark, image, text, color, text_thickness)
