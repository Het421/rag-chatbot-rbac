from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings

# Initialize LLM
llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL_NAME,
    temperature=0.2,
    max_tokens=1024
)

# Output parser — extracts plain string from LLM response
output_parser = StrOutputParser()

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful internal company assistant. 
Your job is to answer employee questions using ONLY the provided context from company documents.

Rules:
- Answer ONLY based on the provided context
- If the answer is not in the context, say "I could not find relevant information in the available documents."
- Be concise and clear
- Always mention which document and page your answer comes from
- Do not make up information"""),

    ("human", """Context from company documents:
{context}

Conversation history:
{history}

Employee question: {question}

Please provide a helpful answer based on the context above.""")
])

# LangChain chain: prompt → llm → parse output
rag_chain = prompt | llm | output_parser


def format_context(chunks: list[dict]) -> str:
    """
    Formats retrieved chunks into a readable context string
    that we pass to the LLM.
    """
    if not chunks:
        return "No relevant documents found."

    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[Source {i+1}: {chunk['filename']}, Page {chunk['page_number']}]\n"
            f"{chunk['chunk_text']}"
        )

    return "\n\n".join(context_parts)


def format_history(conversation_history: list[dict]) -> str:
    """
    Formats recent conversation history for the LLM.
    """
    if not conversation_history:
        return "No previous conversation."

    recent = conversation_history[-6:]  # last 3 exchanges
    lines = []
    for msg in recent:
        role = "Employee" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}")

    return "\n".join(lines)


def extract_sources(chunks: list[dict]) -> list[dict]:
    """
    Extracts unique source citations from retrieved chunks.
    Returns list of {filename, page_number} for storing with the message.
    """
    seen = set()
    sources = []

    for chunk in chunks:
        key = f"{chunk['filename']}_{chunk['page_number']}"
        if key not in seen:
            seen.add(key)
            sources.append({
                "filename": chunk["filename"],
                "page_number": chunk["page_number"]
            })

    return sources


def generate_answer(
    question: str,
    chunks: list[dict],
    conversation_history: list[dict] = []
) -> dict:
    """
    Main function — takes a question + retrieved chunks,
    generates an answer using Groq LLM via LangChain.

    Returns:
        {
            "answer": "...",
            "sources": [{"filename": "...", "page_number": 1}, ...]
        }
    """
    context = format_context(chunks)
    history = format_history(conversation_history)

    answer = rag_chain.invoke({
        "context": context,
        "history": history,
        "question": question
    })

    sources = extract_sources(chunks)

    return {
        "answer": answer,
        "sources": sources
    }