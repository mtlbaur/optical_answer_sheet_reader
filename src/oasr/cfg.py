import logging

debug_enabled = None
debug_form_indexes = None

logging_level = logging.INFO

outpath = "out"
cfgpath = "cfg"

mark_pos_rel_tol = 0.25  # 0.2 worked before, using a more generous 0.25 now since we can correct slightly rotated pages
mark_area_rel_tol = 0.25  # less than 0.2 is probably not a good idea
rotated_mark_pos_rel_tol = 0.05  # 0.01 might be too low

dpi = 300
degrees_rotation = 0
darkness_threshold = 128
