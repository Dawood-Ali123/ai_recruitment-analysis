from langchain_groq import ChatGroq
from app.core.config import settings
from app.schemas.evaluation_report import EvaluationReport
llm = ChatGroq(
    model=settings.GROQ_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0,
    max_retries=2
)

structured_llm = llm.with_structured_output(EvaluationReport)