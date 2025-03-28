from oasr.utility import dict_append

# bounds format: [xl, xr, yt, yb]
last_name_bounds = [0, 9, 0, 25]
first_name_bounds = [11, 20, 0, 25]
field_1_bounds = [22, 31, 0, 25]
field_2_bounds = [33, 42, 0, 9]
field_3_bounds = [33, 42, 14, 23]
questions_bounds = [1, 40, 26, 45]
questions_subregions = [
    [1, 5, 26, 35],
    [8, 12, 26, 35],
    [15, 19, 26, 35],
    [22, 26, 26, 35],
    [29, 33, 26, 35],
    [36, 40, 26, 35],
    [1, 5, 36, 45],
    [8, 12, 36, 45],
    [15, 19, 36, 45],
    [22, 26, 36, 45],
    [29, 33, 36, 45],
    [36, 40, 36, 45],
]

ord_A = ord("A")
ord_0 = ord("0")


def init():
    return {
        "error": {},
        "last_name": {},
        "first_name": {},
        "field_1": {},
        "field_2": {},
        "field_3": {},
        "questions": {},
    }


def record(data, x, y):
    data_category_key = "error"
    entry_key = entry_value = "?"

    def in_bounds(x, y, xl, xr, yt, yb):
        return x >= xl and x <= xr and y >= yt and y <= yb

    if in_bounds(x, y, *last_name_bounds):
        data_category_key = "last_name"
        entry_key = x + 1
        entry_value = chr(y + ord_A)

    elif in_bounds(x, y, *first_name_bounds):
        data_category_key = "first_name"
        entry_key = x - first_name_bounds[0] + 1
        entry_value = chr(y + ord_A)

    elif in_bounds(x, y, *field_1_bounds):
        data_category_key = "field_1"
        entry_key = x - field_1_bounds[0] + 1
        entry_value = chr(y + ord_A)

    elif in_bounds(x, y, *field_2_bounds):
        data_category_key = "field_2"
        entry_key = x - field_2_bounds[0] + 1
        entry_value = chr(y + ord_0)

    elif in_bounds(x, y, *field_3_bounds):
        data_category_key = "field_3"
        entry_key = x - field_3_bounds[0] + 1
        entry_value = chr(y - 14 + ord_0)

    elif in_bounds(x, y, *questions_bounds):
        for i, subregion in enumerate(questions_subregions):
            if in_bounds(x, y, *subregion):
                data_category_key = "questions"

                if i < 6:
                    entry_key = 10 * i + y - subregion[2] + 1
                else:
                    entry_key = 10 * (i - 6) + y - subregion[2] + 61

                entry_value = chr(x - subregion[0] + ord_A)

    else:
        entry_key = (x, y)

    dict_append(data[data_category_key], entry_key, entry_value)

    return (entry_key, entry_value)


def sort(data, *args, **kwargs):
    def dfs(dfs, x):
        if type(x) == list:
            return sorted(x, *args, **kwargs)

        if type(x) == dict:
            for k in x.keys():
                x[k] = dfs(dfs, x[k])

            return dict(sorted(x.items(), *args, **kwargs))

        return x

    for k in data.keys():
        data[k] = dfs(dfs, data[k])

    return data
