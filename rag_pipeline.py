"""Query the existing academic Pinecone index with the notebook's RAG setup."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore


NO_ANSWER = "I couldn't find this information in the provided study material."


class ConfigurationError(Exception):
    """Raised when required RAG configuration is missing."""


class RetrievalError(Exception):
    """Raised when the existing Pinecone index cannot be queried."""


class GenerationError(Exception):
    """Raised when the Groq model cannot generate an answer."""


PROMPT = ChatPromptTemplate.from_template(
    """You are an academic assistant.

Answer the question using ONLY the provided context.

Instructions:
- Give a clear and concise academic answer.
- Explain the concept in simple language.
- Use bullet points when appropriate.
- Use normal text for mathematical expressions where possible.
- Do not invent information.
- If the answer is not present in the context, say:
  "I couldn't find this information in the provided study material."

Context:
{context}

Question:
{question}

Answer:
"""
)


@lru_cache(maxsize=1)
def _get_rag_components():
    """Create query-time clients once; never create or populate the index."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(env_path)

    missing_keys = [
        key
        for key in ("PINECONE_API_KEY", "GROQ_API_KEY")
        if not os.getenv(key)
    ]
    if missing_keys:
        raise ConfigurationError(
            "Missing required environment variable(s): " + ", ".join(missing_keys)
        )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    try:
        vector_store = PineconeVectorStore.from_existing_index(
            index_name=os.getenv("PINECONE_INDEX_NAME", "academic-rag"),
            embedding=embeddings,
        )
    except Exception as exc:
        raise RetrievalError(
            "Could not connect to the existing Pinecone index. Check its name, "
            "Pinecone credentials, and network connection."
        ) from exc

    llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    return vector_store, llm


def ask_question(question, document_ids=None):
    """Return a grounded answer and its retrieved LangChain documents."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Enter a question before asking.")

    vector_store, llm = _get_rag_components()

    try:
        if document_ids:
            sources = vector_store.similarity_search(
                question.strip(),
                k=3,
                filter={
                    "document_id": {
                        "$in": document_ids
                    }
                }
            )
        else:
            sources = vector_store.similarity_search(
                question.strip(),
                k=3
            )
    except Exception as exc:
        raise RetrievalError(
            "The study material could not be searched. Check your Pinecone "
            "connection and try again."
        ) from exc

    if not sources:
        return NO_ANSWER, []

    context = "\n\n".join(document.page_content for document in sources)
    messages = PROMPT.invoke({"context": context, "question": question.strip()})

    try:
        response = llm.invoke(messages)
    except Exception as exc:
        raise GenerationError(
            "The answer service could not respond. Check your Groq API key and "
            "try again."
        ) from exc

    return response.content, sources