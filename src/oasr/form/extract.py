import logging
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv

from tabulate import tabulate

from oasr import cfg
from oasr.utility import trace, format_exception, get_images_from_pdf, get_blank_image, random_color
from .mark import (
    aligns_with,
    find_marks,
    find_matching_edge_marks,
    find_fill_marks,
    draw_contours,
    draw_edge_mark_circles,
    draw_edge_mark_indexes,
    draw_edge_marks,
    draw_fill_mark,
)
from oasr.form import form

lmark_count = 46
bmark_count = 43


def extract(
    *,
    path,
    mark_pos_rel_tol,
    mark_area_rel_tol,
    rotated_mark_pos_rel_tol,
    dpi,
    degrees_rotation,
    darkness_threshold,
):
    trace("extract")

    min_contour_area = dpi * 1.5
    max_contour_area = dpi * 5

    try:
        forms = {}
        images = get_images_from_pdf(path, dpi, degrees_rotation)

        for image_num, image in enumerate(images):
            debug = cfg.debug_enabled and (not cfg.debug_form_indexes or image_num in cfg.debug_form_indexes)

            try:
                marks = find_marks(image, min_contour_area, max_contour_area, darkness_threshold)

                if debug:
                    # base

                    plt.figure(f"base[{image_num}]")
                    plt.imshow(image)

                    # contours

                    contours_image = get_blank_image(image)

                    plt.figure(f"contours[{image_num}]")
                    draw_contours(contours_image, marks, random_color)
                    plt.imshow(contours_image)

                lmarks = find_matching_edge_marks(marks, "l", lmark_count, "contour_area", mark_pos_rel_tol, mark_area_rel_tol)
                bmarks = find_matching_edge_marks(marks, "b", bmark_count, "contour_area", mark_pos_rel_tol, mark_area_rel_tol)

                if len(lmarks) != lmark_count or len(bmarks) != bmark_count:
                    table = []

                    if len(lmarks) != lmark_count:
                        table.append(["left", len(lmarks), lmark_count])

                    if len(bmarks) != bmark_count:
                        table.append(["bottom", len(bmarks), bmark_count])

                    if debug:
                        marks_image = get_blank_image(image)

                        plt.figure(f"marks[{image_num}]")

                        draw_edge_marks(marks_image, lmarks, "r", (0, 127, 255))
                        draw_edge_marks(marks_image, bmarks, "t", (0, 255, 127))

                        error_msg = "invalid edge mark count(s)"

                        plt.imshow(marks_image)
                        plt.title("ERROR: " + error_msg)
                        plt.show()

                    raise ValueError(error_msg + ":\n" + tabulate(table, headers=["side", "found", "expected"]))

                def compute_rot_shift_diffs():
                    xdiff = (bmarks[-1].x - bmarks[0].x) + (bmarks[0].x - lmarks[-1].x) * 1.25
                    ydiff = (lmarks[-1].y - lmarks[0].y) + (bmarks[0].y - lmarks[-1].y) * 1.25

                    return xdiff, ydiff

                def rot_shape_v1():  # unused
                    xdiff, ydiff = compute_rot_shift_diffs()

                    points = [[m.x, m.y] for m in lmarks + bmarks]
                    points.extend([[m.x + xdiff, m.y] for m in lmarks])
                    points.extend([[m.x, m.y - ydiff] for m in bmarks])

                    return points

                def rot_shape_v2():
                    xdiff, ydiff = compute_rot_shift_diffs()

                    return [
                        [lmarks[0].x, lmarks[0].y],
                        [lmarks[-1].x, lmarks[-1].y],
                        [bmarks[0].x, bmarks[0].y],
                        [bmarks[-1].x, bmarks[-1].y],
                        # shifted
                        [lmarks[0].x + xdiff, lmarks[0].y],
                        [lmarks[-1].x + xdiff, lmarks[-1].y],
                        [bmarks[0].x, bmarks[0].y - ydiff],
                        [bmarks[-1].x, bmarks[-1].y - ydiff],
                    ]

                rot_shape_min_area_rect = cv.minAreaRect(np.float32(rot_shape_v2()))

                if debug:
                    marks_image = get_blank_image(image)

                    plt.figure(f"rotation_marks[{image_num}]")

                    draw_edge_mark_circles(marks_image, lmarks, (0, 127, 255))
                    draw_edge_mark_circles(marks_image, bmarks, (0, 255, 127))
                    draw_edge_mark_indexes(marks_image, lmarks)
                    draw_edge_mark_indexes(marks_image, bmarks)

                    cv.drawContours(marks_image, [np.int32(cv.boxPoints(rot_shape_min_area_rect))], 0, (255, 0, 0))

                    plt.imshow(marks_image)

                angle = rot_shape_min_area_rect[2]
                (h, w) = image.shape[:2]

                rotated_image = cv.warpAffine(
                    image,
                    cv.getRotationMatrix2D((w // 2, h // 2), angle, 1.0),
                    (w, h),
                    flags=cv.INTER_CUBIC,
                    borderMode=cv.BORDER_REPLICATE,
                )

                if debug:
                    plt.figure(f"rotated_base[{image_num}]")
                    plt.imshow(rotated_image)

                marks = find_marks(rotated_image, min_contour_area, max_contour_area, darkness_threshold)
                lmarks = find_matching_edge_marks(marks, "l", lmark_count, "contour_area", rotated_mark_pos_rel_tol, mark_area_rel_tol)
                bmarks = find_matching_edge_marks(marks, "b", bmark_count, "contour_area", rotated_mark_pos_rel_tol, mark_area_rel_tol)

                if len(lmarks) != lmark_count or len(bmarks) != bmark_count:
                    table = []

                    if len(lmarks) != lmark_count:
                        table.append(["left", len(lmarks), lmark_count])

                    if len(bmarks) != bmark_count:
                        table.append(["bottom", len(bmarks), bmark_count])

                    if debug:
                        rotated_marks_image = get_blank_image(image)

                        plt.figure(f"rotated_marks[{image_num}]")

                        draw_edge_marks(rotated_marks_image, lmarks, "r", (0, 127, 255))
                        draw_edge_marks(rotated_marks_image, bmarks, "t", (0, 255, 127))

                        error_msg = "invalid edge mark count(s)"

                        plt.imshow(rotated_marks_image)
                        plt.title("ERROR: " + error_msg)
                        plt.show()

                    raise ValueError(error_msg + ":\n" + tabulate(table, headers=["side", "found", "expected"]))

                if debug:
                    rotated_marks_image = get_blank_image(image)
                    draw_edge_marks(rotated_marks_image, bmarks, "t", (0, 255, 127))
                    draw_edge_marks(rotated_marks_image, lmarks, "r", (0, 127, 255))

                fmarks = find_fill_marks(marks, lmarks, bmarks)

                data = form.init()

                for fill_mark in fmarks:
                    for y, left_mark in enumerate(lmarks):
                        if aligns_with(left_mark, fill_mark, "y"):
                            for x, bottom_mark in enumerate(bmarks):
                                if aligns_with(bottom_mark, fill_mark, "x"):
                                    entry_key, entry_value = form.record(data, x, y)

                                    if debug:
                                        draw_fill_mark(rotated_marks_image, fill_mark, f"{entry_key}:{entry_value}", random_color())

                if debug:
                    plt.figure(f"rotated_marks[{image_num}]")
                    plt.imshow(rotated_marks_image)
                    plt.show()

                forms[image_num] = form.sort(data)

            except Exception as e:
                logging.error(f"EXCEPTION: images[{image_num}]:\n{format_exception(e)}")

                if image_num == 0:
                    raise Exception("an exception was raised while the key image was being processed")

    except Exception as e:
        logging.error(format_exception(e))

    return forms
