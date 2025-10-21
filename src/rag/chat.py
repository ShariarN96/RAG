# import lancedb
# import streamlit as st
# from dotenv import load_dotenv
# from openai import OpenAI

# # Load environment variables
# load_dotenv()

# # Initialize OpenAI client
# client = OpenAI()


# # Initialize LanceDB connection
# @st.cache_resource
# def init_db():
#     """Initialize database connection.

#     Returns:
#         LanceDB table object
#     """
#     db = lancedb.connect("data/lancedb")
#     return db.open_table("docling")


# def get_context(query: str, table, num_results: int = 5) -> str:
#     """Search the database for relevant context.

#     Args:
#         query: User's question
#         table: LanceDB table object
#         num_results: Number of results to return

#     Returns:
#         str: Concatenated context from relevant chunks with source information
#     """
#     results = table.search(query).limit(num_results).to_pandas()
#     contexts = []

#     for _, row in results.iterrows():
#         # Extract metadata
#         filename = row["metadata"]["filename"]
#         page_numbers = row["metadata"]["page_numbers"]
#         title = row["metadata"]["title"]

#         # Build source citation
#         source_parts = []
#         if filename:
#             source_parts.append(filename)
#         if page_numbers is not None and len(page_numbers) > 0:
#             source_parts.append(f"p. {', '.join(str(p) for p in page_numbers)}")

#         source = f"\nSource: {' - '.join(source_parts)}"
#         if title:
#             source += f"\nTitle: {title}"

#         contexts.append(f"{row['text']}{source}")

#     return "\n\n".join(contexts)


# def get_chat_response(messages, context: str) -> str:
#     """Get streaming response from OpenAI API.

#     Args:
#         messages: Chat history
#         context: Retrieved context from database

#     Returns:
#         str: Model's response
#     """
#     system_prompt = f"""You are a helpful assistant that answers questions based on the provided context.
#     Use only the information from the context to answer questions. If you're unsure or the context
#     doesn't contain the relevant information, say so.

#     Context:
#     {context}
#     """

#     messages_with_context = [{"role": "system", "content": system_prompt}, *messages]

#     # Create the streaming response
#     stream = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages_with_context,
#         temperature=0.1,
#         stream=True,
#     )

#     # Use Streamlit's built-in streaming capability
#     response = st.write_stream(stream)
#     return response


# # Initialize Streamlit app
# st.title("📚 Document Q&A")

# # Initialize session state for chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Initialize database connection
# table = init_db()

# # Display chat messages
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Chat input
# if prompt := st.chat_input("Ask a question about the document"):
#     # Display user message
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})

#     # Get relevant context
#     with st.status("Searching document...", expanded=False) as status:
#         context = get_context(prompt, table)
#         st.markdown(
#             """
#             <style>
#             .search-result {
#                 margin: 10px 0;
#                 padding: 10px;
#                 border-radius: 4px;
#                 background-color: #f0f2f6;
#             }
#             .search-result summary {
#                 cursor: pointer;
#                 color: #0f52ba;
#                 font-weight: 500;
#             }
#             .search-result summary:hover {
#                 color: #1e90ff;
#             }
#             .metadata {
#                 font-size: 0.9em;
#                 color: #666;
#                 font-style: italic;
#             }
#             </style>
#         """,
#             unsafe_allow_html=True,
#         )

#         st.write("Found relevant sections:")
#         for chunk in context.split("\n\n"):
#             # Split into text and metadata parts
#             parts = chunk.split("\n")
#             text = parts[0]
#             metadata = {
#                 line.split(": ")[0]: line.split(": ")[1]
#                 for line in parts[1:]
#                 if ": " in line
#             }

#             source = metadata.get("Source", "Unknown source")
#             title = metadata.get("Title", "Untitled section")

#             st.markdown(
#                 f"""
#                 <div class="search-result">
#                     <details>
#                         <summary>{source}</summary>
#                         <div class="metadata">Section: {title}</div>
#                         <div style="margin-top: 8px;">{text}</div>
#                     </details>
#                 </div>
#             """,
#                 unsafe_allow_html=True,
#             )

#     # Display assistant response first
#     with st.chat_message("assistant"):
#         # Get model response with streaming
#         response = get_chat_response(st.session_state.messages, context)

#     # Add assistant response to chat history
#     st.session_state.messages.append({"role": "assistant", "content": response})


import json

import lancedb
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Load env vars (.env must contain OPENAI_API_KEY)
load_dotenv()
client = OpenAI()


# -------------------------------
# Initialize LanceDB connection
# -------------------------------
@st.cache_resource
def init_db():
    db = lancedb.connect("data/lancedb")
    return db.open_table("docling")  # must match embedding script


def get_context(query: str, table, num_results: int = 5):
    """Retrieve context rows from LanceDB"""
    results = table.search(query).limit(num_results).to_pandas()
    contexts = []

    for _, row in results.iterrows():
        # Parse metadata JSON (string → dict of original CSV row)
        try:
            metadata = json.loads(row["metadata"])
        except Exception:
            metadata = {}

        # Build a readable metadata display
        meta_str = " | ".join(
            [f"{k}: {v}" for k, v in metadata.items() if v is not None]
        )

        # Append combined result
        contexts.append({"text": row["text"], "metadata": meta_str})

    return contexts


def get_chat_response(messages, context: str) -> str:
    """Ask GPT with retrieved context"""
    system_prompt = f"""You are a helpful assistant that answers questions based on the provided context.
Use only the information from the context to answer questions. The context is a csv file that summarizes metal organic frameworks (MOF) used in oxygen evolution reaction. All data are extracted from research articles.  If the context doesn’t contain the answer, say so.

Context:
{context}
"""

    messages_with_context = [{"role": "system", "content": system_prompt}, *messages]

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_with_context,
        temperature=0.1,
        stream=True,
    )
    response = st.write_stream(stream)
    return response


# -------------------------------
# Streamlit UI
# -------------------------------
st.title("📊 CSV Q&A with LanceDB")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Open table
table = init_db()

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask a question about the CSV data"):
    # User message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Retrieve context
    with st.status("🔎 Searching CSV embeddings..."):
        results = get_context(prompt, table)

        st.write("### Top Matches")
        for r in results:
            st.markdown(
                f"""
                <div style="margin:10px; padding:10px; border:1px solid #ccc; border-radius:6px; background:#f9f9f9;">
                    <b>Context:</b> {r["text"]}<br>
                    <span style="font-size:0.9em; color:#666;">{r["metadata"]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Join texts into one context string for GPT
        context_text = "\n\n".join([r["text"] for r in results])

    # Assistant response
    with st.chat_message("assistant"):
        response = get_chat_response(st.session_state.messages, context_text)

    st.session_state.messages.append({"role": "assistant", "content": response})
