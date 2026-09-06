"""Exploratory side-analysis: scores GPT-4o diagnosis results (from
`diagnosis_pipeline.py`) by top-k PE hit rate. Not part of the core diagnosis
pipeline used for the study's headline results.

For each of the 3 escalating question phases (Q1/Q1+2/Q1+2+3), reports what
fraction of patients had "pulmonary embolism" appear within the top-k
(k=1..5) of the model's differential diagnosis list, aggregated across the
whole `<lang>Results<lang>.csv` file.
"""

import csv


def rows_count():
    """Return the number of data rows in openaiResultsE.csv."""
    with open("openaiResultsE.csv") as file:
        file_object = csv.DictReader(file)
    return sum(1 for row in file_object)


def get_accuracy(result_file):
    """Compute top-1..top-5 PE hit rates for each question phase in `result_file`.

    Args:
        result_file: path to an `openaiResults*.csv` file produced by
            `diagnosis_pipeline.py`, with "Question1"/"Question12"/"Question123"
            columns holding each phase's stringified top-5 diagnosis list.

    Returns:
        A list of three dicts (one per phase), each mapping "k1".."k5" to the
        percentage of patients with PE ranked at or above that position.
        Note: the 18 known non-PE ("Does not have pe") patient rows are
        excluded from both the numerator (via the `count` skip-list) and the
        denominator (`row_count - 18`).
    """
    file_name = (
        result_file[0:-4].split("Results")[0] + result_file[0:-4].split("Results")[1]
    )

    data = 0
    with open(result_file) as file:
        file_object = csv.DictReader(file)
        row_count = sum(1 for row in file_object)
    with open(result_file) as file:
        reader = csv.DictReader(file)
        file.seek(0)
        count = 1
        accuracy_q1 = {"k1": 0, "k2": 0, "k3": 0, "k4": 0, "k5": 0}
        accuracy_q2 = {"k1": 0, "k2": 0, "k3": 0, "k4": 0, "k5": 0}
        accuracy_q3 = {"k1": 0, "k2": 0, "k3": 0, "k4": 0, "k5": 0}

        for row in reader:
            question1 = row["Question1"]
            question12 = row["Question12"]
            question123 = row["Question123"]
            answer1 = question1[2:-2].split(",")
            answer12 = question12[2:-2].split(",")
            answer123 = question123[2:-2].split(",")
            all_answers = [answer1, answer12, answer123]

            q = 1
            # Row numbers (1-indexed) of the 18 patients known NOT to have PE;
            # they are excluded so accuracy only reflects PE-positive patients.
            if count not in (
                4,
                5,
                6,
                8,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
            ):
                for answer in all_answers:
                    print(count)
                    index = 0
                    while index < 5:
                        print(answer[index])
                        if "pulmonary embolism" in answer[index].lower():
                            if index <= 4:
                                if q == 1:
                                    accuracy_q1["k5"] += 1
                                elif q == 2:
                                    accuracy_q2["k5"] += 1
                                elif q == 3:
                                    accuracy_q3["k5"] += 1
                            if index <= 3:
                                if q == 1:
                                    accuracy_q1["k4"] += 1
                                elif q == 2:
                                    accuracy_q2["k4"] += 1
                                elif q == 3:
                                    accuracy_q3["k4"] += 1
                            if index <= 2:
                                if q == 1:
                                    accuracy_q1["k3"] += 1
                                elif q == 2:
                                    accuracy_q2["k3"] += 1
                                elif q == 3:
                                    accuracy_q3["k3"] += 1
                            if index <= 1:
                                if q == 1:
                                    accuracy_q1["k2"] += 1
                                elif q == 2:
                                    accuracy_q2["k2"] += 1
                                elif q == 3:
                                    accuracy_q3["k2"] += 1
                            if index == 0:
                                if q == 1:
                                    accuracy_q1["k1"] += 1
                                elif q == 2:
                                    accuracy_q2["k1"] += 1
                                elif q == 3:
                                    accuracy_q3["k1"] += 1
                        index += 1
                    q += 1
            count += 1

    data = [accuracy_q1, accuracy_q2, accuracy_q3]

    q = 0
    for values in data:
        q += 1
        print(f"Question {q}, {file_name}")
        for item in values:
            # Convert raw hit counts into percentages over the PE-positive cohort.
            data[q - 1][item] = values[item] / (row_count - 18) * 100
            k = item.split("k")[1]
            print(f"""{k}, {data[q - 1][item]}""")

    return data


get_accuracy("openaiResultsE.csv")
get_accuracy("openaiResultsT.csv")
# get_accuracy("anthropicResultsE.csv")
# get_accuracy("anthropicResultsT.csv")
# get_accuracy("groqResultsE.csv")
# get_accuracy("groqResultsT.csv")
