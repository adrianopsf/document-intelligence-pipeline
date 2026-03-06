"""Pipeline integration tests."""

from docai.schemas.extraction import StructuredExtractionSchema


class TestExtractionSchema:
    def test_schema_validates_full(self) -> None:
        data = {
            "document_type": "contract",
            "beneficiary_name": "João da Silva",
            "company_name": "Acme Corp",
            "issue_date": "2024-01-15",
            "due_date": "2024-02-15",
            "total_amount": "R$ 15.000,00",
            "taxes": None,
            "assets": None,
            "obligations": "Prestação de serviços",
            "summary": "Contrato de prestação de serviços entre partes.",
        }
        result = StructuredExtractionSchema(**data)
        assert result.document_type == "contract"
        assert result.beneficiary_name == "João da Silva"

    def test_schema_allows_nulls(self) -> None:
        result = StructuredExtractionSchema()
        assert result.document_type is None
        assert result.beneficiary_name is None

    def test_schema_partial_data(self) -> None:
        result = StructuredExtractionSchema(
            document_type="invoice",
            total_amount="R$ 500,00",
        )
        assert result.document_type == "invoice"
        assert result.total_amount == "R$ 500,00"
        assert result.company_name is None
