"""Document classifier service.

Classifies documents by type using keyword heuristics (MVP).
Designed to be upgraded to LLM-based classification.
"""

from docai.core.logging import get_logger

logger = get_logger(__name__)

DOCUMENT_TYPES = {
    "contract": [
        "contrato", "contract", "cláusula", "clause", "partes contratantes",
        "contratante", "contratado", "vigência", "rescisão", "obrigações",
        "agreement", "hereby", "parties", "terms and conditions",
    ],
    "invoice": [
        "nota fiscal", "invoice", "fatura", "nf-e", "valor total",
        "total amount", "bill to", "payment terms", "due date", "quantidade",
    ],
    "financial_report": [
        "balanço", "demonstração", "balance sheet", "income statement",
        "receita", "revenue", "patrimônio", "equity", "ativo", "passivo",
        "financial statement", "fiscal year", "quarterly report",
    ],
    "legal": [
        "processo", "tribunal", "lawsuit", "court", "sentença", "acórdão",
        "petição", "mandado", "jurisprudência", "legal opinion", "defendant",
        "plaintiff", "judgment", "ruling",
    ],
    "receipt": [
        "recibo", "receipt", "comprovante", "pagamento efetuado",
        "payment received", "transaction", "confirmation",
    ],
}


def classify_document(text: str) -> str:
    """Classify document type based on keyword matching.

    Returns the document type with the highest keyword match count.
    Falls back to 'other' if no strong match.
    """
    text_lower = text.lower()
    scores: dict[str, int] = {}

    for doc_type, keywords in DOCUMENT_TYPES.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[doc_type] = score

    if not scores:
        return "other"

    best_type = max(scores, key=scores.get)  # type: ignore[arg-type]
    logger.info("document_classified", doc_type=best_type, score=scores[best_type])
    return best_type
