"""Exploratory side-analysis: embedding-similarity of patient text vs. a
"Pulmonary Embolism" anchor. Not part of the core diagnosis pipeline used for
the study's headline results.

Generates OpenAI embeddings for patient history text (per phase: history-only,
+exam, +labs) and compares each phase's embedding to a fixed "Pulmoner
Embolizm" reference embedding via cosine distance, to see whether later phases
(with more clinical context) trend closer to the PE concept than earlier ones.
"""

import csv
import os

import numpy as np
from dotenv import find_dotenv, load_dotenv
from langchain_openai import OpenAIEmbeddings
from scipy.spatial.distance import cosine

_ = load_dotenv(find_dotenv())
api_key = os.environ.get("OPENAI_API_KEY")


def get_y(y):
    """Embed the reference string `y` (e.g. "Pulmoner Embolizm") and cache it to disk."""
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
    )

    arr = np.array(embeddings.embed_query(y))
    np.save("peEmbedding.npy", arr)


def get_distance(patient_embeddings, y):
    """Compare each patient's 3 phase embeddings against reference embedding `y`.

    Args:
        patient_embeddings: array of shape (n_patients, 3, embedding_dim), one
            row per patient with phase-1/2/3 embeddings.
        y: the reference embedding (e.g. the PE-concept embedding from `get_y`).

    Prints and returns (via saved .npy) the fraction of patients for which each
    successive phase is closer to `y` than the previous one, as a rough signal
    of whether adding clinical context moves the embedding toward "PE".
    """
    distances = {}

    p = 1
    for patient in patient_embeddings:
        distances.update({f"Patient {p}": []})
        print(f"Patient {p}")
        for v in patient:
            d = cosine(v, y)
            distances[f"Patient {p}"].append(d)
        p += 1

    comparisons = [0, 0, 0]
    for p in distances:
        if distances[p][0] > distances[p][1]:
            comparisons[0] += 1
        if distances[p][0] > distances[p][2]:
            comparisons[1] += 1
        if distances[p][1] > distances[p][2]:
            comparisons[2] += 1

    print("Comparison \n", comparisons)

    pe_cases = patient_embeddings.shape[0]
    ratios = []
    for num in comparisons:
        ratios.append(num / pe_cases)

    ratios = np.array(ratios)
    print(ratios)
    np.save("ratios.npy", ratios)


def embedding_generator(file_name):
    """Embed each patient's cumulative history text for phases 1, 1+2, and 1+2+3.

    Args:
        file_name: path to a patient CSV with "Question1"/"Question2"/"Question3"
            columns (history, exam, labs).

    Returns:
        np.ndarray of shape (n_included_patients, 3, embedding_dim). Patients
        listed in the row-number skip list below (known non-PE cases) are
        excluded.
    """
    arr = []
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
    )

    with open(file_name) as file:
        reader = csv.DictReader(file)
        p = 1
        for row in reader:
            # Row numbers (1-indexed) of patients known NOT to have PE, skipped
            # so the embedding comparison only covers PE-positive cases.
            if p not in (
                17,
                34,
                53,
                54,
                55,
                60,
                62,
                76,
                94,
                95,
                96,
                100,
                102,
                103,
                105,
                108,
                110,
                111,
                112,
                113,
            ):
                q1 = row["Question1"]
                q2 = row["Question1"] + row["Question2"]
                q3 = row["Question1"] + row["Question2"] + row["Question3"]
                vectors = embeddings.embed_documents([q1, q2, q3])
                arr.append(vectors)
            else:
                print("Does not have pe")
            p += 1
    return np.array(arr)


# This script is run as a series of manual, one-off steps rather than a single
# pipeline: generate + cache the patient embeddings once (below, normally
# commented out since embeddingsT.npy already exists), generate + cache the
# reference embedding once via get_y(), then compare using the cached .npy
# files.
# turkishEmbeddings = embedding_generator("turkishPatient.csv")
# np.save('embeddingsT.npy', turkishEmbeddings)

# get_y("Pulmoner Embolizm")

get_distance(
    np.load("embeddingsT.npy", allow_pickle=True),
    np.load("peEmbedding.npy", allow_pickle=True),
)
