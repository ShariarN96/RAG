# AI-Driven Research Discovery via Retrieval-Augmented Generation (RAG)

This project implements an AI-powered research chatbot designed to accelerate literature reviews and provide domain-specific research insights from full-text Wiley articles. It combines a scalable ETL pipeline, advanced text processing/embeddings, and LLM-powered conversational retrieval to streamline the discovery of scientific knowledge.

---
## ⚠️ Disclaimer
This project is intended **solely for academic research purposes** and was developed as part of coursework/research at the **University of Illinois Chicago (UIC)**.  
Permission to use Wiley’s **Text and Data Mining (TDM) services** has been granted through UIC’s institutional subscription and agreement with Wiley, in accordance with their API guidelines.  
Any reproduction, redistribution, or reuse of this project, or the concepts demonstrated within, requires prior approval from Wiley and strict adherence to their API terms and conditions.  
👉 Learn more: [Wiley Text and Data Mining Services](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining)

## 🚀 Features
- **ETL Pipeline**  
  - **Crossref Lookup** → Finds and validates Wiley DOIs
  - **Wiley API Retrieval** → Downloads full-text PDFs using identified DOIs
  - **Azure Blob Storage** → Stores documents securely for downstream use
  - **Automation** → Current pipeline handles ingestion and organization; **Prefect** will be integrated **in the future** for orchestration and workflow automation

- **Document Processing & Embeddings**  
  - Uses **Docling** for text cleaning, chunking, and preprocessing  
  - Generates **vector embeddings** for efficient retrieval  

- **Conversational AI Chatbot**  
  - Integrates **OpenAI LLMs** for context-aware Q&A  
  - Delivers **domain-specific insights** based on uploaded articles  
  - Supports interactive queries for literature discovery  

---

## 🛠️ Tech Stack
- **Languages & Frameworks:** Python, Streamlit
- **Data Engineering:** Azure Blob Storage, ETL Pipelines  
- **Text Processing:** Docling  
- **AI/ML:** OpenAI LLMs
- **APIs:** Wiley API, Crossref










