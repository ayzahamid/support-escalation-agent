import uuid
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from schemas import _EscalationLLMOutput, EscalationResult

_SYSTEM = """You are an escalation specialist at a bank.
A customer's issue could not be resolved by the automated support system and requires human intervention.

Write a clear escalation summary for the human agent who will handle this case.
Include:
- A concise explanation of the customer's issue
- What was already attempted by the automated system
- The recommended immediate action for the human agent
- An urgency level: low, medium, or high"""

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM),
    (
        "human",
        "Category: {category} | Priority: {priority}\n\n"
        "Customer issue:\n{input}\n\n"
        "Automated support response:\n{support_response}",
    ),
])


class EscalationAgent:
    def __init__(self, llm: ChatOpenAI):
        self.chain = _PROMPT | llm.with_structured_output(_EscalationLLMOutput)

    def run(
        self,
        user_input: str,
        category: str,
        priority: str,
        support_response: str,
    ) -> EscalationResult:
        llm_output: _EscalationLLMOutput = self.chain.invoke({
            "input": user_input,
            "category": category,
            "priority": priority,
            "support_response": support_response,
        })
        return EscalationResult(
            ticket_id=f"ESC-{uuid.uuid4().hex[:8].upper()}",
            **llm_output.model_dump(),
        )
