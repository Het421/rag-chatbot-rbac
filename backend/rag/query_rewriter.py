from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import settings

# Initialize LangChain's Groq LLM
llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL_NAME,
    temperature=0.1,
    max_tokens=150
)

# Define the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a search query optimizer for a company internal document system.
Your job is to rewrite user questions into clear, detailed search queries that will find the most relevant information in company documents.

Rules:
- Make the query more specific and detailed
- Expand abbreviations and vague terms
- Keep it as a question or search phrase
- Return ONLY the rewritten query, nothing else
- Do not answer the question, just rewrite it"""),

    ("human", """Rewrite this query to be more search-friendly for finding information in company documents.

Previous conversation context:
{history_context}

Original query: {original_query}

Rewritten query:""")
])

# LangChain chain: prompt → llm
rewriter_chain = prompt | llm


def rewrite_query(original_query: str, conversation_history: list[dict] = []) -> str:
    """
    Rewrites the user's raw query into a more search-friendly version.
    """
    # Build context from recent conversation (last 3 exchanges)
    history_context = "No previous context."
    if conversation_history:
        recent = conversation_history[-6:]
        lines = []
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        history_context = "\n".join(lines)

    response = rewriter_chain.invoke({
        "history_context": history_context,
        "original_query": original_query
    })

    return response.content.strip()