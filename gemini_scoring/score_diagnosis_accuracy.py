"""Post-processing utilities for Gemini pulmonary embolism (PE) diagnosis results.

This script scores the raw per-patient Gemini outputs (`gemini_flash*.csv`) against
the ground truth that every patient in this study has a confirmed PE diagnosis.
For each of the three diagnostic phases (d1/d2/d3 - see METHODOLOGY.md for the
phase definitions), it records:
  - whether "pulmonary embolism" ("pulmoner emboli" in Turkish) appears anywhere in
    the model's top-5 differential diagnosis list ("evet"/"hayir" = yes/no), and
  - the 1-indexed rank/position at which PE appears in that list, if any.

The results are written to a `<file_name>_final.csv` file for downstream accuracy
analysis (e.g. top-k hit rate).
"""

import csv


def top5(file_name):
    """Flag whether PE is present anywhere in each phase's top-5 diagnosis list.

    Args:
        file_name: CSV base name (without ".csv") containing the raw Gemini
            results, with "diagnosis1"/"diagnosis2"/"diagnosis3" columns holding
            the model's top-5 differential diagnoses as a stringified list.

    Returns:
        dict with keys "d1", "d2", "d3", each a list of "evet"/"hayir" strings
        (one per patient row) indicating whether PE was among that phase's top 5.
    """
    pe = ["pulmonary embolism", "pulmoner emboli"]
    top5_d1 = []
    top5_d2 = []
    top5_d3 = []
    top5_final = {"d1": [], "d2": [], "d3": []}

    with open(f"{file_name}.csv") as file:
        reader = csv.DictReader(file)
        for row in reader:
            diagnosis1 = row["diagnosis1"].lower()
            diagnosis2 = row["diagnosis2"].lower()
            diagnosis3 = row["diagnosis3"].lower()

            if (pe[0] in diagnosis1) or (pe[1] in diagnosis1):
                top5_d1.append("evet")
            else:
                top5_d1.append("hayir")
            if (pe[0] in diagnosis2) or (pe[1] in diagnosis2):
                top5_d2.append("evet")
            else:
                top5_d2.append("hayir")
            if (pe[0] in diagnosis3) or (pe[1] in diagnosis3):
                top5_d3.append("evet")
            else:
                top5_d3.append("hayir")

    top5_final["d1"] = top5_d1
    top5_final["d2"] = top5_d2
    top5_final["d3"] = top5_d3

    return top5_final

def top5_pos(file_name):
    """Find the rank (1-5) at which PE appears in each phase's diagnosis list.

    Mirrors `top5`, but instead of a yes/no flag, records the 1-indexed position
    of the first PE match within each patient's top-5 list (empty string if PE
    does not appear in that list).

    Args:
        file_name: CSV base name (without ".csv") containing the raw Gemini
            results, same format as `top5`.

    Returns:
        dict with keys "pos1", "pos2", "pos3", each a list of positions
        (int or "") aligned with the phase-1/2/3 diagnosis columns.
    """
    pe = ["pulmonary embolism", "pulmoner emboli"]
    top5_pos_result = {"pos1": [], "pos2": [], "pos3": []}

    with open(f"{file_name}.csv") as file:
        reader = csv.DictReader(file)
        for row in reader:
            diagnosis1 = row["diagnosis1"][1:].lower().split(",")
            diagnosis2 = row["diagnosis2"][1:].lower().split(",")
            diagnosis3 = row["diagnosis3"][1:].lower().split(",")
            all_diagnosis = [diagnosis1, diagnosis2, diagnosis3]

            list_num = 1
            embolism = False
            for list in all_diagnosis:
                pos = 1
                for diagnosis in list:
                    if (pe[0] in diagnosis) or (pe[1] in diagnosis):
                        p = pos
                        embolism = True
                    if pos == 5 and embolism:
                        top5_pos_result[f"pos{list_num}"].append(p)
                    elif pos == 5:
                        top5_pos_result[f"pos{list_num}"].append("")

                    pos = pos+1
                list_num = list_num + 1

    return top5_pos_result

def to_csv(file_name):
    """Combine `top5` and `top5_pos` results and write them to `<file_name>_final.csv`.

    Note: the row count (177) is hardcoded to this dataset's known patient count
    rather than derived from the input file.

    Args:
        file_name: CSV base name (without ".csv") of the raw Gemini results to
            summarize; output is written to "<file_name>_final.csv".
    """
    top5_f = top5(file_name)
    pos_result = top5_pos(file_name)
    for i in range(177):
        with open(f"{file_name}_final.csv", "a") as file:
                writer = csv.DictWriter(file, fieldnames =["Patient","d1","pos1","d2", "pos2", "d3", "pos3"])
                writer.writerow(
                    {
                        "Patient": i+1,
                        "d1": top5_f["d1"][i],
                        "pos1": pos_result["pos1"][i],
                        "d2": top5_f["d2"][i],
                        "pos2": pos_result["pos2"][i],
                        "d3": top5_f["d3"][i],
                        "pos3": pos_result["pos3"][i]
                    }
                )


# Entry point: summarize the "light" Gemini model's results into
# gemini_flash_light_final.csv.
to_csv("gemini_flash_light")
