import flet as ui
import logging

from pathlib import Path
from datetime import datetime

from oasr import cfg
from oasr.utility import read_data, write_data, format_exception, open_explorer_at_path
from oasr.ui.threading import LoggingHandler, Manager
from oasr.form.read import read


def init():
    page: ui.Page = None
    manager = Manager()

    def save(controls):
        try:
            write_data(
                f"./{cfg.cfgpath}/oasr.cfg",
                {k: v.value for k, v in controls.items()},
            )
        except Exception as e:
            logging.warning(format_exception(e))

    def load(controls):
        try:
            if type(data := read_data(f"./{cfg.cfgpath}/oasr.cfg")) is dict:
                for k, v in data.items():
                    controls[k].value = v
        except Exception as e:
            logging.warning(format_exception(e))

    def start_f(e):
        def get_outfile_types():
            types = []

            if write.value:
                if write_pdf.value:
                    types.append("pdf")
                if write_csv.value:
                    types.append("csv")
                if write_json.value:
                    types.append("json")

            return types

        def get_sorted_debug_form_indexes():
            indexes = []

            for x in debug_form_indexes.value.split():
                if x.isdigit():
                    x = int(x)

                    if not x in indexes:
                        indexes.append(x)

            return sorted(indexes)

        manager.execute(
            {
                "function": read,
                "kwargs": {
                    "infile_path": infile_path.value,
                    "cache_path": cache_path.value,
                    "outfile_name": outfile_name.value,
                    "outfile_types": get_outfile_types(),
                    "debug_form_indexes": get_sorted_debug_form_indexes(),
                    "write_results": write.value,
                    "plot_enabled": plot.value,
                    "debug_enabled": debug.value,
                    "open_outpath_enabled": auto_open_outpath.value,
                    "write_cache": write_cache.value,
                    "load_cache": load_cache.value,
                    "dpi": dpi.value,
                    "degrees_rotation": rotation.value,
                    "darkness_threshold": darkness.value,
                },
            }
        )

    def stop_f(e):
        manager.terminate()

    def clear_fields_f(e):
        for c in [
            infile_path,
            cache_path,
            outfile_name,
            debug_form_indexes,
            log,
        ]:
            c.value = None

    def clear_log_f(e):
        log.controls = []

    def reset_options_f(e):
        for c in [write, write_pdf, write_csv, write_json, auto_open_outpath]:
            c.value = True

        for c in [plot, debug, write_cache, load_cache]:
            c.value = False

        rotation.value = 0.0
        dpi.value = 300.0
        darkness.value = 128.0
        theme.value = 0.0
        theme_change_f(theme.value)

    def start_cb(e):
        start_f(e)

    def stop_cb(e):
        stop_f(e)

    def open_outpath_cb(e):
        open_explorer_at_path(cfg.outpath)

    def clear_fields_cb(e):
        clear_fields_f(e)
        page.update()

    def clear_log_cb(e):
        clear_log_f(e)
        page.update()

    def reset_options_cb(e):
        clear_fields_f(e)
        clear_log_f(e)
        reset_options_f(e)
        page.update()

    def shutdown_f(e):
        stop_f(e)
        save(controls_to_save)

    def window_event_cb(e):
        match e.data:
            case "close":
                shutdown_f(e)
                page.window.destroy()

    def log_cb(r):
        log.controls.extend(
            [
                ui.Text(f"{r.levelname}:{r.getMessage()}", selectable=True),
                ui.Divider(),
            ]
        )
        page.update()

    def clear_cb(e):
        e.control.data.value = None
        page.update()

    def chosen_file_cb(e: ui.FilePickerResultEvent, control):
        if e.files:
            control.value = Path(e.files[0].path).as_posix()
            page.update()

    def get_theme_label_f(index):
        return f"{['System', 'Light', 'Dark'][index]} Theme"

    def get_theme_mode_f(index):
        return [ui.ThemeMode.SYSTEM, ui.ThemeMode.LIGHT, ui.ThemeMode.DARK][index]

    def theme_change_f(value):
        theme.label = get_theme_label_f(int(value))
        page.theme_mode = get_theme_mode_f(int(value))

    def theme_change_cb(e):
        theme_change_f(e.control.value)
        page.update()

    def generate_outfile_name_cb(e):
        outfile_name.value = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + (f"_{Path(infile_path.value).stem}" if infile_path.value != "" else "")

        page.update()

    infile_path = ui.TextField(label="Infile Path", expand=True)
    cache_path = ui.TextField(label="Cache Path", expand=True)
    outfile_name = ui.TextField(label="Outfile Name", expand=True)
    debug_form_indexes = ui.TextField(label="Debug Form Indexes", expand=True)

    dpi = ui.Slider(value=300, label="{value} DPI", min=100, max=1000, divisions=9)
    rotation = ui.Slider(value=0, label="{value}° Rotation", min=-180, max=180, divisions=4)
    darkness = ui.Slider(value=128, label="{value} Darkness Threshold", min=0, max=255, divisions=16)
    theme = ui.Slider(value=0, min=0, max=2, divisions=2, on_change=theme_change_cb)

    write = ui.Checkbox(label="Write", value=True)
    write_pdf = ui.Checkbox(label="PDF", value=True)
    write_csv = ui.Checkbox(label="CSV", value=True)
    write_json = ui.Checkbox(label="JSON", value=True)

    plot = ui.Checkbox(label="Plot")
    debug = ui.Checkbox(label="Debug")
    auto_open_outpath = ui.Checkbox("Open Outpath", value=True)

    write_cache = ui.Checkbox(label="Write Cache")
    load_cache = ui.Checkbox(label="Load Cache")

    infile_path_file_picker = ui.FilePicker(on_result=lambda e: chosen_file_cb(e, infile_path))
    cache_path_file_picker = ui.FilePicker(on_result=lambda e: chosen_file_cb(e, cache_path))

    infile_path_file_picker_button = ui.Button(text="Select", on_click=infile_path_file_picker.pick_files)
    cache_path_file_picker_button = ui.Button(text="Select", on_click=cache_path_file_picker.pick_files)

    outfile_name_generate_button = ui.Button(text="Generate", on_click=generate_outfile_name_cb)

    clear_infile_path = ui.Button(text="Clear", on_click=clear_cb, data=infile_path)
    clear_cache_path = ui.Button(text="Clear", on_click=clear_cb, data=cache_path)
    clear_outfile_name = ui.Button(text="Clear", on_click=clear_cb, data=outfile_name)
    clear_debug_form_indexes = ui.Button(text="Clear", on_click=clear_cb, data=debug_form_indexes)

    log = ui.ListView(auto_scroll=True, expand=True)

    start = ui.Button(text="Start", on_click=start_cb)
    stop = ui.Button(text="Stop", on_click=stop_cb)
    open_outpath = ui.Button(text="Open Outpath", on_click=open_outpath_cb)
    clear_fields = ui.Button(text="Clear Fields", on_click=clear_fields_cb)
    clear_log = ui.Button(text="Clear Log", on_click=clear_log_cb)
    reset_options = ui.Button(text="Default", on_click=reset_options_cb)

    controls_to_save = {
        "infile_path": infile_path,
        "cache_path": cache_path,
        "outfile_name": outfile_name,
        "debug_form_indexes": debug_form_indexes,
        #
        "dpi": dpi,
        "rotation": rotation,
        "darkness": darkness,
        "theme": theme,
        #
        "write": write,
        "write_pdf": write_pdf,
        "write_csv": write_csv,
        "write_json": write_json,
        #
        "plot": plot,
        "debug": debug,
        "auto_open_outpath": auto_open_outpath,
        #
        "write_cache": write_cache,
        "load_cache": load_cache,
    }

    def main(initialized_page: ui.Page):
        nonlocal page
        page = initialized_page

        logging.basicConfig(format="%(levelname)s: %(message)s", level=cfg.logging_level)
        logging_handler = LoggingHandler(manager, log_cb, level=cfg.logging_level)
        logging.getLogger().addHandler(logging_handler)

        load(controls_to_save)

        # center page for 1920x1080
        w, h, s = 1920, 1080, 0.8
        w, h = w * s, h * s
        x, y = 1920 / 2 - w / 2, 1080 / 2 - h / 2

        page.window.width = w
        page.window.height = h

        page.window.left = x
        page.window.top = y

        page.window.prevent_close = True
        page.window.on_event = window_event_cb
        page.title = "Optical Answer Sheet Reader"

        page.overlay.extend(
            [
                infile_path_file_picker,
                cache_path_file_picker,
            ]
        )

        page.add(
            ui.Row(
                [
                    ui.Column(
                        [
                            ui.Row([infile_path, infile_path_file_picker_button, clear_infile_path]),
                            ui.Row([cache_path, cache_path_file_picker_button, clear_cache_path]),
                            ui.Row([outfile_name, outfile_name_generate_button, clear_outfile_name]),
                            ui.Row([debug_form_indexes, clear_debug_form_indexes]),
                            ui.Container(content=log, border=ui.border.all(), expand=True, padding=10),
                        ],
                        expand=True,
                    ),
                    ui.Column(
                        [
                            ui.Row([write, write_pdf, write_csv, write_json]),
                            ui.Row([plot, debug, auto_open_outpath]),
                            ui.Row([write_cache, load_cache]),
                            ui.Row([clear_fields, clear_log, reset_options]),
                            ui.Row([start, stop, open_outpath]),
                            ui.Row([dpi]),
                            ui.Row([rotation]),
                            ui.Row([darkness]),
                            ui.Row([theme]),
                        ],
                    ),
                ],
                expand=True,
            )
        )

        theme_change_f(theme.value)

        page.update()  # this is for the above theme_change_f() call to prevent the UI from getting out of sync with theme state

        page.window.visible = True

    ui.app(target=main, view=ui.FLET_APP_HIDDEN)
