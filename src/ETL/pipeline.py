from pathlib import Path

import pandas as pd

from RAG.src.blob_utils.from_blob import save_wiley_pdf_to_blob
from RAG.src.ETL.blob_load import delete_blob, generate_sas_url, list_blob
from RAG.src.ETL.crossref import add_dois
from RAG.src.rag.qa import add_row, ask_llm
from RAG.src.rag.utils.chunking import chunks_from_pdf

if __name__ == "__main__":
    add_dois()
    new_dois = Path(__file__).parent.parent.parent.parent / "doi.csv"
    df = pd.read_csv(new_dois)
    df = df.drop_duplicates()
    df.to_csv(new_dois, index=False)
    new_dois = Path(__file__).parent.parent.parent.parent / "doi.csv"
    avilable_dois = Path(__file__).parent.parent.parent.parent / "output.csv"
    # current_dois = (
    #     pd.read_csv(avilable_dois)
    #     .drop_duplicates(subset=["doi"])
    #     .to_csv(avilable_dois, index=False)
    # )
    current_dois = pd.read_csv(avilable_dois)["doi"].tolist()
    coming_dois = list(set(pd.read_csv(new_dois)["DOI"].tolist()))

    for doi in coming_dois:
        if str(doi).split(".")[-1] not in [str(x).split(".")[-1] for x in current_dois]:
            # print(f"Processing new DOI: {doi}")

            save_wiley_pdf_to_blob(doi)

    articles = list_blob()

    for article in articles:
        pdf_path = generate_sas_url(article)
        context = chunks_from_pdf(pdf_path)
        if context is None:
            print(f"artcile with doi of {article} not processed")
        if "MOF" not in context:
            continue
        result = ask_llm(context)
        add_row(result)
    delete_blob()
