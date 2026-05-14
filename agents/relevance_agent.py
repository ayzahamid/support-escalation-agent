from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from schemas import RelevanceResult

_SYSTEM = """You are a query relevance checker for a bank's customer support system.
Determine whether the user's message is related to banking services such as:
accounts, cards, loans, transactions, online banking, fees, statements, fraud, or transfers.

Unrelated queries (weather, cooking, general knowledge, etc.) are NOT relevant."""

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM),
    ("human", "{input}"),
])


class RelevanceAgent:
    def __init__(self, llm: ChatOpenAI):
        self.chain = _PROMPT | llm.with_structured_output(RelevanceResult)

    def run(self, user_input: str) -> RelevanceResult:
        return self.chain.invoke({"input": user_input})
