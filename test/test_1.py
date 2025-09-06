from oasr import cfg

cfg.debug_enabled = False


def test_test1():
    from oasr.form.extract import extract
    from oasr.form.process import process

    results = process(
        extract(
            path="./form/test1.pdf",
            mark_pos_rel_tol=cfg.mark_pos_rel_tol,
            mark_area_rel_tol=cfg.mark_area_rel_tol,
            rotated_mark_pos_rel_tol=cfg.rotated_mark_pos_rel_tol,
            dpi=cfg.dpi,
            degrees_rotation=cfg.degrees_rotation,
            darkness_threshold=cfg.darkness_threshold,
        )
    )

    scores = results["scores"]

    x = scores[0]

    assert x["last_name"] == "ABCZYXWAYZ"
    assert x["first_name"] == "ABCRQPPYZA"
    assert x["field_1"] == "ARSTUVWXYZ"
    assert x["field_2"] == "9876543210"
    assert x["field_3"] == "0123456789"

    assert x["correct"] == 120
    assert x["wrong"] == 0
    assert x["empty"] == 0
    assert x["invalid"] == 0

    assert x["correct_list"] == ["1A", "2B", "3C", "4D", "5E", "6D", "7C", "8B", "9A", "10B", "11C", "12D", "13E", "14D", "15C", "16B", "17A", "18B", "19C", "20D", "21E", "22D", "23C", "24B", "25A", "26B", "27C", "28D", "29E", "30D", "31C", "32B", "33A", "34B", "35C", "36D", "37E", "38D", "39C", "40B", "41A", "42B", "43C", "44D", "45E", "46D", "47C", "48B", "49A", "50B", "51C", "52D", "53E", "54D", "55C", "56B", "57A", "58B", "59C", "60D", "61E", "62D", "63C", "64B", "65A", "66B", "67C", "68D", "69E", "70D", "71C", "72B", "73A", "74B", "75C", "76D", "77E", "78D", "79C", "80B", "81A", "82B", "83C", "84D", "85E", "86D", "87C", "88B", "89A", "90B", "91C", "92D", "93E", "94D", "95C", "96B", "97A", "98B", "99C", "100D", "101E", "102D", "103C", "104B", "105A", "106B", "107C", "108D", "109E", "110D", "111C", "112B", "113A", "114B", "115C", "116D", "117E", "118D", "119C", "120B"]
    assert x["wrong_list"] == []
    assert x["empty_list"] == []
    assert x["invalid_list"] == []

    assert x["log"] == []

    x = scores[1]

    assert x["last_name"] == "A_Z"
    assert x["first_name"] == "Z_A"
    assert x["field_1"] == "A_Z"
    assert x["field_2"] == "9_0"
    assert x["field_3"] == "0_9"

    assert x["correct"] == 3
    assert x["wrong"] == 21
    assert x["empty"] == 96
    assert x["invalid"] == 0

    assert x["correct_list"] == ["1A", "41A", "81A"]
    assert x["wrong_list"] == ["10E", "11A", "20E", "21A", "30E", "31A", "40E", "50E", "51A", "60E", "61A", "70E", "71A", "80E", "90E", "91A", "100E", "101A", "110E", "111A", "120E"]
    assert x["empty_list"] == ["2", "3", "4", "5", "6", "7", "8", "9", "12", "13", "14", "15", "16", "17", "18", "19", "22", "23", "24", "25", "26", "27", "28", "29", "32", "33", "34", "35", "36", "37", "38", "39", "42", "43", "44", "45", "46", "47", "48", "49", "52", "53", "54", "55", "56", "57", "58", "59", "62", "63", "64", "65", "66", "67", "68", "69", "72", "73", "74", "75", "76", "77", "78", "79", "82", "83", "84", "85", "86", "87", "88", "89", "92", "93", "94", "95", "96", "97", "98", "99", "102", "103", "104", "105", "106", "107", "108", "109", "112", "113", "114", "115", "116", "117", "118", "119"]
    assert x["invalid_list"] == []

    assert x["log"] == []

    x = scores[2]

    assert x["last_name"] == "Z_A"
    assert x["first_name"] == "A_Z"
    assert x["field_1"] == "Z_A"
    assert x["field_2"] == "0_9"
    assert x["field_3"] == "9_0"

    assert x["correct"] == 3
    assert x["wrong"] == 21
    assert x["empty"] == 96
    assert x["invalid"] == 0

    assert x["correct_list"] == ["21E", "61E", "101E"]
    assert x["wrong_list"] == ["1E", "10A", "11E", "20A", "30A", "31E", "40A", "41E", "50A", "51E", "60A", "70A", "71E", "80A", "81E", "90A", "91E", "100A", "110A", "111E", "120A"]
    assert x["empty_list"] == ["2", "3", "4", "5", "6", "7", "8", "9", "12", "13", "14", "15", "16", "17", "18", "19", "22", "23", "24", "25", "26", "27", "28", "29", "32", "33", "34", "35", "36", "37", "38", "39", "42", "43", "44", "45", "46", "47", "48", "49", "52", "53", "54", "55", "56", "57", "58", "59", "62", "63", "64", "65", "66", "67", "68", "69", "72", "73", "74", "75", "76", "77", "78", "79", "82", "83", "84", "85", "86", "87", "88", "89", "92", "93", "94", "95", "96", "97", "98", "99", "102", "103", "104", "105", "106", "107", "108", "109", "112", "113", "114", "115", "116", "117", "118", "119"]
    assert x["invalid_list"] == []

    assert x["log"] == []
