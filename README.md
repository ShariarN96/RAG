# AI-Driven Research Discovery via Retrieval-Augmented Generation (RAG)

This project implements an AI-powered research chatbot** designed to accelerate literature reviews and provide domain-specific research insights from full-text Wiley articles.  
It combines a scalable ETL pipeline, advanced text processing/embeddings, and LLM-powered conversational retrieval to streamline the discovery of scientific knowledge.

---
## ⚠️ Disclaimer
This project is intended **solely for academic and research purposes**.  
Permission has been granted by **Wiley** to use their **Text and Data Mining (TDM) services** in accordance with their API guidelines.  
Any reproduction, redistribution, or reuse of this project—or the concepts demonstrated within—requires prior approval from **Wiley** and strict adherence to their **API terms and conditions**.

## 🚀 Features
- **ETL Pipeline**  
  - Retrieves full-text PDFs from the **Wiley API**  
  - Stores documents securely in **Azure Blob Storage**  
  - Handles automated ingestion and organization  

- **Document Processing & Embeddings**  
  - Uses **Docling** for text cleaning, chunking, and preprocessing  
  - Generates **vector embeddings** for efficient retrieval  

- **Conversational AI Chatbot**  
  - Integrates **OpenAI LLMs** for context-aware Q&A  
  - Delivers **domain-specific insights** based on uploaded articles  
  - Supports interactive queries for literature discovery  

---

## 🛠️ Tech Stack
- **Languages & Frameworks:** Python, Streamlit (for UI, optional)  
- **Data Engineering:** Azure Blob Storage, ETL Pipelines  
- **Text Processing:** Docling  
- **AI/ML:** OpenAI LLMs, vector embeddings  
- **APIs:** Wiley API, Crossref


