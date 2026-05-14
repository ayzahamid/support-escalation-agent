from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from schemas import SupportResult
from tools import TOOLS

_SYSTEM = """You are an expert bank customer support agent.

You have access to two tools:
- search_faq: look up bank policies, procedures, and common questions
- check_known_issues: check for active system incidents that may explain a problem

Rules:
1. ALWAYS query the relevant tool before composing your answer.
2. For technical complaints, use check_known_issues first.
3. For policy or procedure questions, use search_faq first.
4. Be empathetic, clear, and concise in your response.
5. If you cannot fully resolve the issue, end your response with exactly:
   ESCALATION_REQUIRED: <brief reason>
"""

_ESCALATION_MARKER = "escalation_required:"


class SupportAgent:
    def __init__(self, llm: ChatOpenAI):
        self.graph = create_react_agent(llm, TOOLS, prompt=_SYSTEM)

    def run(self, user_input: str, category: str, priority: str) -> SupportResult:
        # Embed context in the human turn so it's visible per-request
        full_input = f"[Category: {category} | Priority: {priority}]\n\n{user_input}"

        result = self.graph.invoke({"messages": [("human", full_input)]})
        messages = result["messages"]

        ai_messages = [m for m in messages if isinstance(m, AIMessage) and m.content]
        response_text: str = ai_messages[-1].content if ai_messages else ""
        tools_used: bool = any(isinstance(m, ToolMessage) for m in messages)

        escalation_needed = (
            _ESCALATION_MARKER in response_text.lower()
            or priority == "critical"
        )

        if escalation_needed:
            # Strip the marker line from the customer-facing response
            clean_lines = [
                line for line in response_text.splitlines()
                if _ESCALATION_MARKER not in line.lower()
            ]
            return SupportResult(
                response="\n".join(clean_lines).strip(),
                resolved=False,
                resolution_note="Escalation required — could not resolve automatically.",
                tools_used=tools_used,
            )

        return SupportResult(
            response=response_text,
            resolved=True,
            resolution_note="Resolved by support agent.",
            tools_used=tools_used,
        )
