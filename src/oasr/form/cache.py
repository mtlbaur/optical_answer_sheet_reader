import logging

from pprint import pformat
from ast import literal_eval

from oasr import cfg
from oasr.utility import format_exception, trace
from oasr.form import form


def save(outfile_name, data):
    trace("cache.save")

    with open(f"./{cfg.outpath}/{outfile_name}_cache.txt", "w") as f:
        print(pformat(data, width=1, sort_dicts=False), file=f)


def load(path):
    trace("cache.load")

    data = None

    with open(path, "r") as f:
        try:
            data = literal_eval(f.read())

            if data and type(data) is dict:
                for k, v in data.items():
                    data[k] = form.sort(v)
        except Exception as e:
            logging.error(format_exception(e))

    return data
