import logging

from oasr.utility import trace, list_to_space_sep_str, get_sorted_dict


def get_categories():
    return {"correct": 0, "wrong": 0, "invalid": 0, "empty": 0}


def get_responses():
    return {"A": get_categories(), "B": get_categories(), "C": get_categories(), "D": get_categories(), "E": get_categories()}


def log_warning(form_num, score, msg):
    logging.warning(f"forms[{form_num}]: {score['first_name']}_{score['last_name']}: {msg}")
    score["log"].append(f"WARNING: {msg}")


def record_field(field_key, form_num, form, score):
    res = []
    last_i = 0

    for i, chars in form[field_key].items():
        if i > last_i + 1:
            res.append("_")

        if len(chars) == 1:
            res.append(chars[0])
        else:
            res.extend(["[", "".join(chars), "]"])

            log_warning(
                form_num,
                score,
                f"field char at index {i} has {len(chars)} responses: {list_to_space_sep_str(chars)}",
            )

        last_i = i

    score[field_key] = "".join(res)


def record_score(score, question_num, response_category, response=[]):
    score[response_category] += 1
    score[response_category + "_list"].append(str(question_num) + "".join(response))


def record_question(questions, question_num, response_category):
    if question_num in questions:
        questions[question_num][response_category] += 1
    else:
        questions[question_num] = get_categories()
        questions[question_num][response_category] = 1


def record_response(responses, question_num, response_category, response):
    response = "".join(response)

    if question_num in responses:
        responses[question_num][response][response_category] += 1
    else:
        responses[question_num] = get_responses()
        responses[question_num][response][response_category] = 1


def process(forms):
    trace("process")

    possible_responses = ["A", "B", "C", "D", "E"]

    data = {"scores": {}, "questions": {}, "responses": {}}

    scores = data["scores"]
    questions = data["questions"]
    responses = data["responses"]

    key_form = forms[0]

    for form_num, form in forms.items():
        score = scores[form_num] = {
            "last_name": "",
            "first_name": "",
            "field_1": "",
            "field_2": "",
            "field_3": "",
            "correct": 0,
            "wrong": 0,
            "invalid": 0,
            "empty": 0,
            "correct_list": [],
            "wrong_list": [],
            "invalid_list": [],
            "empty_list": [],
            "log": [],
        }

        record_field("last_name", form_num, form, score)
        record_field("first_name", form_num, form, score)
        record_field("field_1", form_num, form, score)
        record_field("field_2", form_num, form, score)
        record_field("field_3", form_num, form, score)

        for num, res in form["questions"].items():
            if len(res) == 1:
                if num in key_form["questions"]:
                    if res == key_form["questions"][num]:
                        record_score(score, num, "correct", res)

                        if form_num != 0:
                            record_question(questions, num, "correct")
                            record_response(responses, num, "correct", res)
                    else:
                        record_score(score, num, "wrong", res)

                        if form_num != 0:
                            record_question(questions, num, "wrong")
                            record_response(responses, num, "wrong", res)
            else:
                record_score(score, num, "invalid", res)

                if form_num != 0:
                    record_question(questions, num, "invalid")
                    record_response(responses, num, "invalid", res)

                log_warning(form_num, score, f"question #{num} has {len(res)} responses: {list_to_space_sep_str(res)}")

        for num in key_form["questions"].keys():
            if num not in form["questions"].keys():
                record_score(score, num, "empty")

                if form_num != 0:
                    record_question(questions, num, "empty")

                    for res in possible_responses:
                        record_response(responses, num, "empty", res)

            elif form_num != 0:
                for res in possible_responses:
                    if [res] != form["questions"][num]:
                        record_response(responses, num, "empty", res)

    data["questions"] = get_sorted_dict(data["questions"])
    data["responses"] = get_sorted_dict(data["responses"])

    return data
