from langchain_core.tools import tool

_BANK_FAQ: dict[str, tuple[list[str], str]] = {
    "lost_card": (
        ["lost card", "stolen card", "missing card", "card missing", "lost my card"],
        "If your card is lost or stolen, call 1-800-555-0100 immediately or freeze it in the app "
        "under Card Management > Freeze Card. A replacement card arrives in 3–5 business days.",
    ),
    "password_reset": (
        ["password reset", "forgot password", "can't login", "locked out", "reset password"],
        "To reset your online banking password: visit the login page, click 'Forgot Password', "
        "enter your email, and follow the verification link. After 3 failed attempts your account "
        "is locked for 24 hours for security.",
    ),
    "international_fees": (
        ["international", "foreign transaction", "overseas", "abroad", "foreign fee"],
        "International transactions carry a 3% foreign transaction fee. Premier account holders "
        "enjoy fee-free international transactions.",
    ),
    "overdraft": (
        ["overdraft", "insufficient funds", "negative balance", "overdraw"],
        "Overdraft protection is available as a linked savings account (free) or an overdraft "
        "line of credit ($35/year). Enable it in Settings > Account Protection.",
    ),
    "fraud_dispute": (
        ["fraud", "dispute", "unauthorized charge", "fraudulent", "charge i didn't make"],
        "To dispute a fraudulent charge: open the app, go to Transactions, select the charge, "
        "and tap 'Report as Fraud'. Alternatively call 1-800-555-0200. Disputes are resolved "
        "within 5–10 business days.",
    ),
    "wire_transfer": (
        ["wire transfer", "wire", "send money internationally", "swift"],
        "Domestic wires cost $25; international wires cost $45. Wires submitted before 3 PM ET "
        "process the same day. You'll need the recipient's routing and account numbers.",
    ),
    "direct_deposit": (
        ["direct deposit", "payroll", "employer deposit", "set up deposit"],
        "For direct deposit, provide your employer with Routing Number: 021000021 and your "
        "account number (found in the app under Account Details).",
    ),
    "statement": (
        ["statement", "bank statement", "download statement", "account history"],
        "Statements are available in the app under Statements & Documents. You can download up "
        "to 7 years of statements. Paper statements are mailed monthly.",
    ),
    "monthly_fee": (
        ["monthly fee", "minimum balance", "account fee", "service charge"],
        "Standard checking requires a $500 minimum daily balance to waive the $12 monthly fee. "
        "Premier accounts have no minimum balance or monthly fee.",
    ),
    "close_account": (
        ["close account", "cancel account", "shut down account"],
        "To close an account, visit a branch with government-issued ID. Ensure all pending "
        "transactions are settled and the balance is $0 before closing.",
    ),
}


@tool
def search_faq(query: str) -> str:
    """Search the bank's FAQ knowledge base for answers to common banking questions.
    Use this for policy, procedure, and general information questions."""
    query_lower = query.lower()
    matches: list[str] = []

    for _key, (keywords, answer) in _BANK_FAQ.items():
        if any(kw in query_lower for kw in keywords):
            matches.append(answer)

    if not matches:
        return (
            "No FAQ entry found for that query. Consider escalating to a human agent "
            "or asking the customer to contact support directly."
        )
    return "\n\n".join(matches)
