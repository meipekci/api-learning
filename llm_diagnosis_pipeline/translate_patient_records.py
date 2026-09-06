"""Parses the raw `PE Patient File.docx` transcript and translates it to English.

The source .docx contains free-text Turkish patient records, one per "Hasta N"
("Patient N") header, each with three question/answer sections plus a
prediction-scores block (Wells, Geneva, PERC, YEARS, PESI). This script splits
the document into per-patient blocks, then uses GPT-4o to translate each
patient's Q&A sections into English and appends the result to
`englishPatient.csv`.

Part of the actual data-preparation step used in this study, producing the
English-language patient records referenced elsewhere in the project.

Note: `PE Patient File.docx` (real, de-identified patient case data) is not
included in this repository and must be supplied separately to run this script.
"""

import csv
import os

from docx import Document
from dotenv import find_dotenv, load_dotenv
from langchain.prompts.chat import ChatPromptTemplate
from langchain_openai import ChatOpenAI

_ = load_dotenv(find_dotenv())

myapi_key = os.environ.get("gptTranslator_key")

llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=myapi_key)


# Load the raw patient transcript document.
document = Document("PE Patient File.docx")

# Initialize an empty list to hold each patient's formatted data
patients_data = []

# Initialize an empty string to collect each patient's information
patient_info = ""

# Group consecutive non-empty paragraphs into one block of text per patient,
# starting a new block whenever a "Hasta N" header line is encountered.
for paragraph in document.paragraphs:
    text = paragraph.text.strip()

    # Check if the text is empty, and skip if so
    if not text:
        continue

    # Detect patient headers, like "Hasta 1", and start a new block for it
    # (skipped on the very first header, since there's no prior block yet).
    if text.startswith("Hasta") and patient_info:
        patients_data.append(patient_info)
        patient_info = ""

    # Concatenate the text for the current patient
    patient_info += text + " "

# Append the last patient's data
if patient_info:
    patients_data.append(patient_info)

# Split each patient's raw block into its Question 1/2/3 and prediction-score
# segments. Note: `structured_data` is built for reference but the actual
# translation loop below re-derives these segments from `patients_data`.
structured_data = [
    f"""Soru 1 - {data.split("Soru 1-")[1].split("Soru 2-")[0].strip()}
    Soru 2 - {data.split("Soru 2-")[1].split("Soru 3-")[0].strip()}
    Soru 3 - {data.split("Soru 3-")[1].split("SONUÇ")[0].strip()}
    Prediction Scores - {data.split("Wells Skoru")[1].strip()}"""
    for idx, data in enumerate(patients_data)
]


# Resume numbering after whatever patients are already in englishPatient.csv,
# so re-running this script on new .docx entries doesn't clobber prior output.
if os.path.exists("englishPatient.csv"):
    with open("englishPatient.csv") as file:
        reader = csv.DictReader(file)
        existing_data = list(reader)
        max_patient_number = max(
            [int(row["Patient"].replace("Patient", "")) for row in existing_data],
            default=0,
        )
else:
    max_patient_number = 0


translate_prompt = ChatPromptTemplate(
    [
        (
            "system",
            """You are an expert linguist and translator, fluent in Turkish and English, with deep cultural 
        understanding of both. Your translations must be accurate, context-aware, and preserve the original tone, nuance, and intent.
        Stick to the given prompt or text as much as possible. You will specifically translating medical documents, so it is important
        to give extremely accurate translation. Also, there will me a lot of medical terminology. If specialized terminology appears,
        use the most precise and widely accepted equivalent. Ensure grammar, punctuation, and syntax are flawless.""",
        ),
        (
            "human",
            """Translate this information into English:
        
        {prompt}"
        """,
        ),
    ]
)


chain = translate_prompt | llm

# Translate each patient's three Q&A sections and prediction-scores block into
# English (one LLM call per field) and append the row to englishPatient.csv.
for idx, data in enumerate(patients_data):
    hasta = f"Patient{max_patient_number + idx + 1}"
    with open("englishPatient.csv", "a") as file:
        writer = csv.DictWriter(
            file, fieldnames=["Hasta", "Soru1", "Soru2", "Soru3", "Scores"]
        )
        writer.writerow(
            {
                "Hasta": hasta,
                "Soru1": chain.invoke(
                    {"prompt": data.split("Soru 1-")[1].split("Soru 2-")[0].strip()}
                ).content,
                "Soru2": chain.invoke(
                    {"prompt": data.split("Soru 2-")[1].split("Soru 3-")[0].strip()}
                ).content,
                "Soru3": chain.invoke(
                    {"prompt": data.split("Soru 3-")[1].split("SONUÇ")[0].strip()}
                ).content,
                "Scores": chain.invoke(
                    {"prompt": f"Wells Skoru: {data.split('Wells Skoru')[1].strip()}"}
                ).content,
            }
        )
    print(hasta)
