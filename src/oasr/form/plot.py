import numpy as np
import matplotlib.pyplot as plt

from oasr.utility import trace

rotation = 45
fontsize = 6
horizontalalignment = "center"


def random_color():
    return np.random.uniform(0.2, 0.8, 3)


def plot_scores(results):
    plt.figure("scores")
    plt.title("number of correct responses per form")

    x = []
    y = []
    colors = []

    for k, v in results["scores"].items():
        x.append(f"{k}_{v['first_name'] + '_' + v['last_name']}")
        y.append(v["correct"])
        colors.append(random_color())

    plt.bar(x, y, color=colors)
    plt.xticks(x, rotation=rotation, fontsize=fontsize, horizontalalignment="right")
    plt.yticks(y, fontsize=fontsize)
    plt.xlabel("index_name")
    plt.ylabel("number correct")
    plt.tight_layout()


def plot_questions(results):
    plt.figure("questions")
    plt.title("number of times a question was answered correctly")

    x = []
    y = []
    colors = []

    for k, v in results["questions"].items():
        x.append(k)
        y.append(v["correct"] if "correct" in v else 0)
        colors.append(random_color())

    plt.bar(x, y, color=colors)
    plt.xticks(x, rotation=rotation, fontsize=fontsize, horizontalalignment=horizontalalignment)
    plt.yticks(y, fontsize=fontsize)
    plt.xlabel("question number")
    plt.ylabel("times correct")
    plt.tight_layout()


def plot_responses(results):
    plt.set_loglevel("warning")

    fig = plt.figure("responses")
    ax = fig.subplots()
    ax.yaxis.get_major_locator().set_params(integer=True)

    plt.title("response categorization")

    color = {"correct": (0, 0.6, 0), "wrong": (0.6, 0, 0), "invalid": (0.6, 0, 0.6), "empty": (0.9, 0.9, 0.9)}
    labeled_categories = set([])

    for num, res in results["responses"].items():
        for res_key, category in res.items():
            if sum(count if cat_key != "empty" else 0 for cat_key, count in category.items()) == 0:
                continue

            offset = 0

            for cat_key, count in category.items():
                bar = plt.bar(
                    f"{num}{res_key}",
                    count,
                    label=cat_key if cat_key not in labeled_categories else "",
                    color=color[cat_key],
                    bottom=offset,
                )
                labeled_categories.add(cat_key)
                offset += count

                if count > 0:
                    ax.bar_label(bar, label_type="center", fontsize=fontsize)

    plt.xticks(plt.xticks()[0], rotation=rotation, fontsize=fontsize, horizontalalignment=horizontalalignment)
    plt.yticks(plt.yticks()[0], fontsize=fontsize)
    plt.xlabel("responses")
    plt.ylabel("count")

    plt.legend()

    plt.tight_layout()

    plt.set_loglevel("info")


def plot(results):
    trace("plot")

    plot_scores(results)
    plot_questions(results)
    plot_responses(results)

    plt.show()
