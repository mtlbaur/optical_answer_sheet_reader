import os
import logging

from time import time
from pathlib import Path

from oasr import cfg
from oasr.utility import trace, open_explorer_at_path
from .extract import extract
from .process import process
from .plot import plot
from .write import write
from . import cache


def read(
    *,
    infile_path="",
    cache_path="",
    outfile_name="",
    debug_form_indexes=[],
    outfile_types=["csv", "json"],
    write_results=False,
    plot_enabled=False,
    debug_enabled=False,
    open_outpath_enabled=False,
    write_cache=False,
    load_cache=False,
    mark_pos_rel_tol,
    mark_area_rel_tol,
    rotated_mark_pos_rel_tol,
    dpi,
    degrees_rotation,
    darkness_threshold,
):
    runtime = 0

    if not debug_enabled:
        starttime = time()

    infile_path = Path(infile_path)

    if debug_enabled:
        cfg.debug_enabled = True

    if debug_form_indexes:
        cfg.debug_form_indexes = debug_form_indexes

    data = None

    if not load_cache:
        data = extract(
            path=infile_path.as_posix(),
            mark_pos_rel_tol=mark_pos_rel_tol,
            mark_area_rel_tol=mark_area_rel_tol,
            rotated_mark_pos_rel_tol=rotated_mark_pos_rel_tol,
            dpi=dpi,
            degrees_rotation=degrees_rotation,
            darkness_threshold=darkness_threshold,
        )
    else:
        if cache_path == "":
            data = cache.load(Path(f"./{cfg.outpath}/{infile_path.stem}_cache.txt").as_posix())
        else:
            data = cache.load(Path(cache_path).as_posix())

    if not data:
        logging.warning("no data")
        return

    if not type(data) is dict:
        logging.warning("type(data) was not a dict")
        return

    if write_results or write_cache:
        if not os.path.isdir(cfg.outpath):
            os.mkdir(cfg.outpath)

    if write_cache:
        cache.save(infile_path.stem, data)

    data = process(data)

    if write_results and outfile_types:
        write(data, outfile_name if outfile_name else infile_path.stem, outfile_types)

        if open_outpath_enabled:
            open_explorer_at_path(cfg.outpath)

    if not debug_enabled:
        runtime += time() - starttime
        trace(f"runtime: {round(runtime, 3)}s")

    if plot_enabled:
        plot(data)

    trace("done")

    return data
