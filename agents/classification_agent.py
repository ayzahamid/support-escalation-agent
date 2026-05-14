from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from schemas import ClassificationResult

_SYSTEM = """You are a support ticket classifier for a bank.

Classify the banking query into one of the following:

Category:
- technical  → app bugs, login failures, website errors, system outages
- billing    → charges, fees, refunds, statements, payment disputes
- general    → account info, product questions, policy inquiries, transfers

Priority:
- low      → minor inconvenience, no financial impact
- medium   → moderate issue, some impact on banking access
- high     → significant access or financial issue
- critical → security breach, large unauthorized transaction, complete account lockout"""

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM),
    ("human", "{input}"),
])


class ClassificationAgent:
    def __init__(self, llm: ChatOpenAI):
        self.chain = _PROMPT | llm.with_structured_output(ClassificationResult)

    def run(self, user_input: str) -> ClassificationResult:
        return self.chain.invoke({"input": user_input})
