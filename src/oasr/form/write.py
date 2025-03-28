import json
import csv
import numpy as np

from copy import deepcopy
from pathlib import Path
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

from oasr import cfg
from oasr.utility import trace, list_to_space_sep_str


def convert(results):
    scores = results["scores"]

    for form_num in scores.keys():
        score = scores[form_num]

        score["correct_list"] = list_to_space_sep_str(score["correct_list"])
        score["wrong_list"] = list_to_space_sep_str(score["wrong_list"])
        score["empty_list"] = list_to_space_sep_str(score["empty_list"])
        score["invalid_list"] = list_to_space_sep_str(score["invalid_list"])

    responses = {}

    for num, res in results["responses"].items():
        for res_key, category in res.items():
            responses[f"{num}{res_key}"] = {}

            for cat_key, count in category.items():
                responses[f"{num}{res_key}"][cat_key] = count

    results["responses"] = responses

    return results


def write_pdf(path, data):
    vspace = 10
    fontsize = 10
    base_style = ParagraphStyle(name="base", fontSize=fontsize)

    digits = 3
    total = data[0]["correct"]
    scores = []

    for k, v in data.items():
        if k > 0:
            scores.append(v["correct"])

    doc = SimpleDocTemplate(path, title=Path(path).stem)
    flow = []

    def extend_flow(text=None, bullet=False, space_x=1, page_break=False):
        nonlocal flow

        if text is not None:
            if bullet:
                flow.append(Paragraph(text, bulletText="-", style=base_style))
            else:
                flow.append(Paragraph(text, style=base_style))

        for _ in range(space_x):
            flow.append(Spacer(0, vspace))

        if page_break:
            flow.append(PageBreak())

    for k, v in data.items():
        name = (v["first_name"] + " " + v["last_name"]).replace("_", " ")
        score = f"{v['correct']}/{total} = {round(v['correct'] / total * 100, digits)}%"

        text = {}

        if k == 0:
            avg = sum(scores) / len(scores)
            std = np.std(scores)

            text["SUMMARY"] = [
                f"{len(scores)} scores: {' '.join(str(x) for x in scores)}",
                f"average: {round(avg, digits)} = {round(avg / total * 100, digits)}%",
                f"standard deviation: {round(std, digits)} = {round(std / total * 100, digits)}%",
            ]

        text["SCORE"] = [f"{name} [{k}]", f"score: {score}"]

        def extend_text_score(key):
            nonlocal text

            if v[key] > 0:
                text["SCORE"] += [f"{v[key]} {key}: {' '.join(x for x in v[f'{key}_list'])}"]

        extend_text_score("correct")
        extend_text_score("wrong")
        extend_text_score("invalid")
        extend_text_score("empty")

        if v["log"]:
            text["SCORE"] += v["log"]

        if "SUMMARY" in text:
            extend_flow("SUMMARY")

            for line in text["SUMMARY"]:
                extend_flow(line, bullet=True)

        extend_flow(text["SCORE"][0])

        for line in text["SCORE"][1:]:
            extend_flow(line, bullet=True)

        extend_flow(page_break=True)

    doc.build(flow)


def write_csv(path, header, data):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)

        for k, v in data.items():
            w.writerow([k] + [x for x in v.values()])


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def write(
    results,
    outfile_name="",
    types=["pdf", "csv", "json"],
):
    trace("write")

    if outfile_name:
        outfile_name += "_"

    if "pdf" in types:
        write_pdf(f"./{cfg.outpath}/{outfile_name}scores.pdf", results["scores"])

    if "csv" in types:
        conv_results = convert(deepcopy(results))

        def write(category, prefix):
            data = conv_results[category]

            write_csv(
                f"./{cfg.outpath}/{outfile_name}{category}.csv",
                [prefix] + [k for k in data[next(iter(data.keys()))]],
                data,
            )

        write("scores", "number")
        write("questions", "number")
        write("responses", "response")

    if "json" in types:
        write_json(f"./{cfg.outpath}/{outfile_name}scores.json", results["scores"])
        write_json(f"./{cfg.outpath}/{outfile_name}questions.json", results["questions"])
        write_json(f"./{cfg.outpath}/{outfile_name}responses.json", results["responses"])
