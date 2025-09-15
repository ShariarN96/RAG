from crossref import add_dois
from 
from RAG.src.blob_utils.from_blob import save_wiley_pdf_to_blob
from RAG.src.rag.qa import main

if __name__ == "__main__":
    dois = add_dois()
    for doi in dois:
        save_wiley_pdf_to_blob(doi)
    
    articles = list_blob()
    main()
