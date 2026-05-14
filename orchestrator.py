import logging
from schemas import PipelineResponse
from agents import RelevanceAgent, ClassificationAgent, SupportAgent, EscalationAgent
from utils import get_llm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("orchestrator")


class Orchestrator:
    """
    Multi-agent pipeline for bank customer support.

    Flow:
        User Query
            → RelevanceAgent   (is this a banking query?)
            → ClassificationAgent (technical / billing / general + priority)
            → SupportAgent     (tool-calling agent: search_faq, check_known_issues)
            → EscalationAgent  (only if unresolved or critical priority)
    """

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.2):
        llm = get_llm(model=model, temperature=temperature)
        self.relevance_agent = RelevanceAgent(llm)
        self.classification_agent = ClassificationAgent(llm)
        self.support_agent = SupportAgent(llm)
        self.escalation_agent = EscalationAgent(llm)

    def handle(self, user_input: str) -> PipelineResponse:
        logger.info("New request: %s", user_input)

        # ── Step 1: Relevance ────────────────────────────────────────────────
        relevance = self.relevance_agent.run(user_input)
        logger.info("[RelevanceAgent] relevant=%s | %s", relevance.relevant, relevance.reason)

        if not relevance.relevant:
            return PipelineResponse(
                status="irrelevant",
                reason=relevance.reason,
            )

        # ── Step 2: Classification ───────────────────────────────────────────
        classification = self.classification_agent.run(user_input)
        logger.info(
            "[ClassificationAgent] category=%s | priority=%s | %s",
            classification.category,
            classification.priority,
            classification.summary,
        )

        # ── Step 3: Support (with tools) ─────────────────────────────────────
        support = self.support_agent.run(
            user_input,
            category=classification.category.value,
            priority=classification.priority.value,
        )
        logger.info(
            "[SupportAgent] resolved=%s | tools_used=%s | %s",
            support.resolved,
            support.tools_used,
            support.resolution_note,
        )

        if support.resolved:
            return PipelineResponse(
                status="resolved",
                category=classification.category.value,
                priority=classification.priority.value,
                response=support.response,
                tools_used=support.tools_used,
            )

        # ── Step 4: Escalation ───────────────────────────────────────────────
        escalation = self.escalation_agent.run(
            user_input,
            category=classification.category.value,
            priority=classification.priority.value,
            support_response=support.response,
        )
        logger.info(
            "[EscalationAgent] ticket=%s | urgency=%s",
            escalation.ticket_id,
            escalation.urgency,
        )

        return PipelineResponse(
            status="escalated",
            category=classification.category.value,
            priority=classification.priority.value,
            response=support.response,
            tools_used=support.tools_used,
            ticket_id=escalation.ticket_id,
            escalation_message=escalation.escalation_message,
            recommended_action=escalation.recommended_action,
            urgency=escalation.urgency,
        )


if __name__ == "__main__":
    orchestrator = Orchestrator()

    queries = [
        "I was charged twice for my monthly fee — I need a refund.",
        "I can't log into the mobile app, it keeps crashing.",
        "How do I set up direct deposit for my paycheck?",
        "What's the best pizza topping?",
        "Someone made unauthorized transactions on my account totaling $5,000!",
    ]

    for query in queries:
        print(f"\n{'─'*60}")
        print(f"Query: {query}")
        result = orchestrator.handle(query)
        print(f"Status : {result.status}")
        if result.category:
            print(f"Category: {result.category} | Priority: {result.priority}")
        if result.response:
            print(f"Response: {result.response[:200]}...")
        if result.ticket_id:
            print(f"Ticket  : {result.ticket_id} ({result.urgency} urgency)")
        if result.reason:
            print(f"Reason  : {result.reason}")
