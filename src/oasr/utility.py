import logging
import traceback
import pdf2image
import numpy as np
import cv2 as cv
import json
import pickle
import logging

from pathlib import Path
from random import randint


def trace(msg):
    logging.info(f"[{msg}]")


def format_exception(e):
    return "".join(traceback.TracebackException.from_exception(e).format())


def get_images_from_pdf(path, dpi, degrees_rotation):
    images = pdf2image.convert_from_path(path, dpi=dpi)

    for i in range(len(images)):
        images[i] = np.array(images[i].rotate(degrees_rotation, expand=1, fillcolor=(255, 255, 255)))

    return images


def get_empty_contour():
    return np.zeros((4, 1, 2), dtype=np.int32)


def get_blank_image(image, color=(0, 0, 0)):
    return np.full(image.shape, color, np.uint8)


def get_black_to_gray_image(image, lower=(0, 0, 0), upper=(128, 128, 128)):
    return cv.inRange(image, lower, upper)


def sort_by(l, attr_name, *args, **kwargs):
    return sorted(l, key=lambda x: getattr(x, attr_name), *args, **kwargs)


def list_to_str(l, sep=" "):
    return sep.join(x for x in l)


def list_to_space_sep_str(l):
    return list_to_str(l, sep=" ")


def dict_add(dictionary, key, value):
    if key in dictionary:
        dictionary[key] += value
    else:
        dictionary[key] = value


def dict_append(dictionary, key, value):
    if key in dictionary:
        dictionary[key].append(value)
    else:
        dictionary[key] = [value]


def get_sorted_dict(dictionary):
    return dict(sorted(dictionary.items()))


def get_json_str(dictionary):
    return json.dumps(dictionary, indent=4)


def random_color(min=0.5, max=1):
    min = int(255 * min)
    max = int(255 * max)
    return (randint(min, max), randint(min, max), randint(min, max))


def invert_color(color):
    return tuple(255 - c for c in color)


def mult_color(color, mult):
    return tuple(min(255, c * mult) for c in color)


def div_color(color, div):
    return tuple(max(0, c / div) for c in color)


def mkdirs_by_filename(filename):
    Path(filename).parent.mkdir(exist_ok=True, parents=True)


def read(filename, r):
    try:
        return r(filename)
    except Exception as e:
        logging.warning(format_exception(e))


def write(filename, data, w, x):
    try:
        mkdirs_by_filename(filename)

        try:
            return w(filename, data)
        except:
            return x(filename, data)
    except Exception as e:
        logging.warning(format_exception(e))


def read_data(filename):
    def r(filename):
        with open(filename, "rb") as file:
            return pickle.load(file)

    return read(filename, r)


def write_data(filename, data):
    def w(filename, data):
        with open(filename, "wb") as file:
            pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)

    def x(filename, data):
        with open(filename, "xb") as file:
            pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)

    write(filename, data, w, x)


def open_explorer_at_path(target):
    from os.path import realpath, exists

    target = Path(realpath(target))

    if exists(target):
        from os import startfile

        startfile(target)
    else:
        logging.warning(f'path "{target.as_posix()}" does not exist')
