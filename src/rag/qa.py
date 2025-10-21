import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

COLUMNS = [
    "doi",
    "year",
    "reaction",
    "catalyst",
    "metal_types",
    "organic_linker",
    "metal_count",
    "crystallinity",
    "morphology",
    "BET_surface_area_m2_per_g",
    "stability_time_hours",
    "stability_current_density_mAcm2",
    "overpotential_mV_at_10mAcm2",
    "tafel_mV_per_dec",
    "electrolyte",
    "stability_notes",
]


# 3. Define your question

question = (
    "Identify the DOI of the paper. "
    "Identify the publication year of the paper. "
    "Identify the reaction (OER, HER, ORR, NO3RR, CO2 reduction) studied in this paper. "
    "Identify the catalyst material studied in this paper.explicitly identify what metals were used."
    "What is the organic linker/ligand they have used for the catalyst"
    "Is it single metal or binary>ternary?"
    "Is it amorphous or crystalline? Set as null if not mentioned"
    "What is the morphology of the catalyst (nanosheets, nanoparticles, nanoclusters, nanorods, nanowires, hollow spheres, etc)"
    "Please identify BET surface area with unit of (m2/g) it it mentioned"
    "stability time: show the duration only in hours of stability experiment"
    "identify current density or voltage of long term stability/durability experiment"
    "find overpotential at 10 mA cm^-2 (report unit in mV or what is mentioned)"
    "Find Tafel slope with unit of (mV/dec)"
    "find electrolyte used"
    "What is the stability results of the catalyst"
    "from this paper and return a tidy JSON list. If a field is missing, use null."
    "Be precise and use only the context I supply."
    "All items should be in individual pairs, not list format or dictionary inside dictionary of lists"
    "Leave as null if not mentioned for any field. if you couldn't find any information about crystallinity, leave it as None"
)
# 4. Send to GPT-4o-mini

# context = chunks_from_pdf()
system_prompt = (
    "You are a helpful assistant that answers questions based on the provided context."
    """Use only the information from the context to answer questions. If you're unsure or the context
    doesn't contain the relevant information, say info doesn't exist. 
        "Use ONLY the supplied context to answer"""
)


def ask_llm(context):
    OpenAI_API_PATH = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(OpenAI_API_PATH)
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")

    client = OpenAI(api_key=OPENAI_KEY)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"},
    ]

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,  # deterministic output
        top_p=1,
        messages=messages,
    )

    answer = resp.choices[0].message.content.strip()
    cleaned = answer.replace("```json", "").replace("```", "").strip()
    data = json.loads(cleaned)

    return data


# def add_row(data):
#     df = pd.DataFrame(columns=COLUMNS)
#     x = []
#     for i in data:
#         x.append(data[i])
#     df.loc[len(df)] = x
#     df.to_csv(
#         "output.csv", mode="a", header=not os.path.exists("output.csv"), index=False
#     )


def add_row(data):
    df = pd.DataFrame(columns=COLUMNS)

    # Collect values into a list
    x = [data[i] for i in data]

    try:
        # Try inserting the row
        df.loc[len(df)] = x

        # Append to CSV (create if it doesn’t exist)
        df.to_csv(
            "output.csv", mode="a", header=not os.path.exists("output.csv"), index=False
        )
    except ValueError as e:
        # Handle mismatched columns without crashing
        print(f"⚠️ Skipping row due to mismatch: {e}")
        print("Row content:", x)  # optional: log the skipped row


def main():
    result = ask_llm()
    add_row(result)


# if __name__ == "__main__":
#     result = ask_llm()
#     add_row(result)


# df = pd.DataFrame(columns=COLUMNS)
# x = []
# for i in result:
#     x.append(result[i])
# df.loc[len(df)] = x
# df.to_csv("output.csv", mode="a", header=not os.path.exists("output.csv"), index=False)
