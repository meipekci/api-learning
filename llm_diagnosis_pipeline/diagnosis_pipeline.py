"""Main diagnosis pipeline: the primary pipeline used to produce this study's
results.

Hardcoded here to GPT-4o via `ChatOpenAI`, but this was the pipeline run
against every model evaluated in this study -- swapping in a different
provider's API key (and adjusting the `ChatOpenAI` model/client
accordingly) was how each model was evaluated.

Reads `turkishPatient.csv` (expected in the working directory) row by row and,
for each patient, asks the model three progressively richer sets of questions
(triage-only, +clinical exam, +labs and risk scores) about the most likely
diagnoses, PE probability, and whether a CT angiography is warranted. Results
are appended to `openaiResultsT.csv`.

Note: `turkishPatient.csv` (real, de-identified patient case data) is not
included in this repository and must be supplied separately to run this script.
"""

import csv
import os

from dotenv import find_dotenv, load_dotenv
from langchain.schema import BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

_ = load_dotenv(find_dotenv())

myapi_key = os.environ.get("OPENAI_API_KEY")


class CommaSeperatedListOutputParser(BaseOutputParser):
    """Parses a comma-separated LLM response (e.g. a list of diagnoses) into a list."""

    def parse(self, text: str):
        return text.strip().split(", ")


llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=myapi_key)


# NOTE: the system prompt below is written in English; the human-turn `{info}`
# is filled in with Turkish patient data (see the CSV read loop). There is
# currently no separate English-language prompt variant.
turkish_prompt = ChatPromptTemplate(
    [
        (
            "system",
            """You are an experienced emergency doctor evaluating patients in the emergency department.
     The clinical information provided below may appear in English, Turkish, or other languages. 
     Accurately interpret all medical content regardless of language.
     Using the clinical information that is provided—including presenting symptoms, medical history, physical findings, 
     and any initial tests—to synthesize a differential diagnosis, assess the likelihood of critical conditions, and determine the most appropriate next steps.
     Base your clinical reasoning on current evidence-based guidelines and decision rules where applicable.
     Ensure your analysis is focused, transparent, and does not assume any data that is not provided. Do not make up information.
     
     Limit responses to additional question to a few words or a simple yes/no answer if possible.
     For example: 
        - Question: "How likely is it that the patient has Pulmonary Embolism?"
        - Answer: "Low Probability" or "Moderate" or "High Probability"
    
     If questions prompt for multiple answers, use this format:
        - Question: "What are the 5 most likely diagnoses in this patient?"
        - Answer: "diagnosis1,diagnosis2,diagnosis3,diagnosis4,diagnosis5"
        Note: Each answer is only seperated by a commma and there are no spaces between answers/commas.
     
     IMPORTANT: 
     - Give the response purely in English even if the question are in a different language. 
     - DO NOT include an sort of introduction or explanation, and only provide.
     
     Use the Pulmonary Embolism (PE) Prediction Scores as a criteria: 
     In the diagnosis of PE, clinical judgment based on experience, along with symptoms, clinical findings, 
    and risk factors for venous thromboembolism (VTE), plays a significant role. However, despite the proven
    value of clinical judgment in large studies, the lack of standardization has led to the development of various following clinical prediction scoring systems:

    WELLS Score:

    - <2: Low probability (3.4%)

    - 2–6: Moderate probability (27.8%)

    - ≥7: High probability (78.4%)

    GENEVA Score:

    - 0–3: Low probability

    - 4–10: Moderate probability

    - ≥11: High probability

    PERC (Pulmonary Embolism Rule-out Criteria):

    - 0: PE probability <1%

    - ≥1: PE cannot be ruled out

    YEARS Criteria:

    - 0 points + D-dimer <1000: Rule out PE

    - ≥1 point + D-dimer <500: Rule out PE

    - 0 points + D-dimer ≥1000: Perform CT

    - ≥1 point + D-dimer ≥500: Perform CT

    30-Day Mortality Risk Scoring (PESI – Pulmonary Embolism Severity Index):

    - Class I: ≤65 points (0–1.6%)

    - Class II: 66–85 points (1.7–3.5%)

    - Class III: 86–105 points (3.2–7.1%)

    = Class IV: 106–125 points (4–11.4%)

    - Class V: >125 points (10–24.5%)
     """,
        ),
        (
            "human",
            """
        {info}
        """,
        ),
    ]
)


patient_num = 1
patient_data = []


# Turkish-language question text sent to the model alongside each patient row.
diagnosis_qt = "Bu hastada hastada en olası 5 tanı nedir?"
prob_qt = "Bu hastada hastada pulmoner emboli olasılığı nedir?"
bt_qt = "Bu hastada pulmoner emboli için toraks BT anjiyo çekmelimiyiz?"

# Build the LangChain pipeline (prompt -> LLM -> parser) and run it once per
# patient row, per question, escalating the amount of clinical context given
# to the model (history only -> +exam -> +labs/risk scores).
with open("turkishPatient.csv") as file:
    reader = csv.DictReader(file)
    chain = turkish_prompt | llm | CommaSeperatedListOutputParser()
    for row in reader:
        result = [
            chain.invoke({"info": f"{row['Question1']} {diagnosis_qt}"}),
            chain.invoke({"info": f"{row['Question1']} {prob_qt}"}),
            chain.invoke(
                {
                    "info": f"{row['Question1']} {row['Question2']}\n{row['Wells']}, {row['Genova']}, {row['PERC']}\n{diagnosis_qt}"
                }
            ),
            chain.invoke(
                {
                    "info": f"{row['Question1']} {row['Question2']}\n{row['Wells']}, {row['Genova']}, {row['PERC']}\n {prob_qt}"
                }
            ),
            chain.invoke(
                {
                    "info": f"{row['Question1']} {row['Question2']}\n{row['Wells']}, {row['Genova']}, {row['PERC']}\n {bt_qt}"
                }
            ),
            chain.invoke(
                {
                    "info": f"{row['Question1']} {row['Question2']} {row['Question3']}\n{row['Wells']}, {row['Genova']}, {row['PERC']}, {row['YEARS']}\n{diagnosis_qt}"
                }
            ),
            chain.invoke(
                {
                    "info": f"{row['Question1']} {row['Question2']} {row['Question3']}\n{row['Wells']}, {row['Genova']}, {row['PERC']}, {row['YEARS']}\n{prob_qt}"
                }
            ),
            chain.invoke(
                {
                    "info": f"{row['Question1']} {row['Question2']} {row['Question3']}\n{row['Wells']}, {row['Genova']}, {row['PERC']}, {row['YEARS']}\n{bt_qt}"
                }
            ),
        ]
        print(patient_num)
        patient_data.append(
            {
                f"Patient": f"Patient {patient_num}",
                "D1": result[0],
                "P1": result[1][0],
                "D2": result[2],
                "P2": result[3][0],
                "bt1": result[4][0],
                "D3": result[5],
                "P3": result[6][0],
                "bt2": result[7][0],
            }
        )
        print(patient_data[patient_num - 1])
        patient_num += 1


def patient_num():
    """Return the highest patient number already present in openaiResultsT.csv.

    Used by `to_csv` to number newly appended patients so repeated runs of this
    script accumulate results rather than overwrite/renumber existing ones.
    Note: this shadows the module-level `patient_num` counter defined above.
    """
    if os.path.exists("openaiResultsT.csv"):
        with open("openaiResultsT.csv") as file:
            reader = csv.DictReader(file)
            existing_data = list(reader)
            max_patient_number = max(
                [int(row["Hasta"].replace("Hasta", "")) for row in existing_data],
                default=0,
            )
    else:
        max_patient_number = 0

    return max_patient_number


def to_csv(data):
    """Append each patient's collected Q&A results to openaiResultsT.csv."""
    patient_number = patient_num()
    for idx, patient in enumerate(data):
        hasta = f"Hasta{patient_number + idx + 1}"
        with open("openaiResultsT.csv", "a") as file:
            writer = csv.DictWriter(
                file, fieldnames=["Patient", "Question1", "Question12", "Question123"]
            )
            writer.writerow(
                {
                    "Patient": patient["Patient"],
                    "Q1Diagnosis": patient["D1"],
                    "Q1Likeliness": patient["P1"],
                    "Q12Diagnosis": patient["D2"],
                    "Q12Likeliness": patient["P2"],
                    "Q12BT": patient["bt1"],
                    "Q123Diagnosis": patient["D3"],
                    "Q123Likeliness": patient["P3"],
                    "Q123BT": patient["bt2"],
                }
            )


to_csv(patient_data)
