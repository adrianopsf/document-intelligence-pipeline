#!/usr/bin/env python3
"""
Generate synthetic sample documents for demo and testing.

Usage:
    python data/samples/generate_samples.py

Requires: pymupdf (already a project dependency)
Output: creates PDF files in the same directory as this script.
"""

from pathlib import Path

import fitz  # PyMuPDF

OUTPUT_DIR = Path(__file__).parent


def make_contract() -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (72, 80),
        "CONTRATO DE PRESTAÇÃO DE SERVIÇOS\n\n"
        "Pelo presente instrumento, as partes abaixo qualificadas celebram\n"
        "o presente Contrato de Prestação de Serviços, regido pelas cláusulas\n"
        "e condições seguintes:\n\n"
        "CONTRATANTE: Acme Corp Ltda.\n"
        "CNPJ: 12.345.678/0001-99\n"
        "Endereço: Av. Paulista, 1000, São Paulo - SP\n\n"
        "CONTRATADO (BENEFICIÁRIO): João da Silva\n"
        "CPF: 123.456.789-00\n\n"
        "OBJETO: Desenvolvimento de software sob demanda.\n\n"
        "CLÁUSULA 1 – DO VALOR E PAGAMENTO\n"
        "O valor total do contrato é de R$ 15.000,00 (quinze mil reais),\n"
        "a ser pago em 3 parcelas mensais de R$ 5.000,00.\n\n"
        "CLÁUSULA 2 – DA VIGÊNCIA\n"
        "O presente contrato vigorará pelo prazo de 12 (doze) meses,\n"
        "a contar da data de assinatura: 2024-01-15.\n"
        "Data de vencimento: 2025-01-15.\n\n"
        "CLÁUSULA 3 – DAS OBRIGAÇÕES DAS PARTES\n"
        "O Contratado se compromete a entregar os serviços conforme\n"
        "especificações técnicas acordadas em anexo.\n\n"
        "CLÁUSULA 4 – DA RESCISÃO\n"
        "Este contrato poderá ser rescindido por qualquer das partes\n"
        "mediante aviso prévio de 30 dias.\n\n"
        "São Paulo, 15 de Janeiro de 2024.\n\n"
        "_______________________          _______________________\n"
        "   Acme Corp Ltda.                   João da Silva\n"
        "    CONTRATANTE                       CONTRATADO\n",
        fontsize=10,
    )
    path = OUTPUT_DIR / "sample_contract.pdf"
    doc.save(str(path))
    doc.close()
    print(f"Created: {path}")


def make_invoice() -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (72, 80),
        "NOTA FISCAL DE SERVIÇOS\n\n"
        "Número: NF-001234\n"
        "Data de Emissão: 2024-02-01\n"
        "Data de Vencimento: 2024-03-01\n\n"
        "EMITENTE:\n"
        "João da Silva - MEI\n"
        "CNPJ: 98.765.432/0001-11\n"
        "Endereço: Rua das Flores, 42, Campinas - SP\n\n"
        "TOMADOR DE SERVIÇOS:\n"
        "Acme Corp Ltda.\n"
        "CNPJ: 12.345.678/0001-99\n\n"
        "DISCRIMINAÇÃO DOS SERVIÇOS:\n"
        "  - Desenvolvimento de API REST (Sprint 1)  R$  3.500,00\n"
        "  - Desenvolvimento de Frontend (Sprint 1)  R$  1.500,00\n\n"
        "VALORES:\n"
        "  Subtotal:                                 R$  5.000,00\n"
        "  ISS (5%):                                 R$    250,00\n"
        "  TOTAL A PAGAR:                            R$  5.250,00\n\n"
        "FORMA DE PAGAMENTO: Transferência Bancária (PIX)\n"
        "Chave PIX: joao.silva@email.com\n\n"
        "Observações: Referente ao mês de Janeiro/2024.\n",
        fontsize=10,
    )
    path = OUTPUT_DIR / "sample_invoice.pdf"
    doc.save(str(path))
    doc.close()
    print(f"Created: {path}")


def make_financial_report() -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (72, 80),
        "DEMONSTRAÇÃO DE RESULTADO DO EXERCÍCIO (DRE)\n"
        "Acme Corp Ltda. — Exercício Fiscal 2023\n\n"
        "RECEITA BRUTA DE VENDAS\n"
        "  Receita de produtos                      R$ 1.200.000,00\n"
        "  Receita de serviços                      R$   350.000,00\n"
        "  TOTAL RECEITA BRUTA                      R$ 1.550.000,00\n\n"
        "DEDUÇÕES DA RECEITA\n"
        "  Impostos sobre vendas (PIS/COFINS/ISS)   R$  (155.000,00)\n"
        "  Devoluções e abatimentos                 R$   (12.000,00)\n"
        "  RECEITA LÍQUIDA                          R$ 1.383.000,00\n\n"
        "CUSTOS E DESPESAS OPERACIONAIS\n"
        "  Custo dos produtos vendidos              R$  (620.000,00)\n"
        "  Despesas com pessoal                     R$  (280.000,00)\n"
        "  Despesas administrativas                 R$   (95.000,00)\n"
        "  Depreciação e amortização                R$   (18.000,00)\n"
        "  RESULTADO OPERACIONAL (EBITDA)           R$   370.000,00\n\n"
        "RESULTADO FINANCEIRO\n"
        "  Receitas financeiras                     R$    22.000,00\n"
        "  Despesas financeiras                     R$   (31.000,00)\n"
        "  RESULTADO ANTES DO IRPJ/CSLL             R$   361.000,00\n\n"
        "  IRPJ e CSLL (34%)                        R$  (122.740,00)\n\n"
        "  LUCRO LÍQUIDO DO EXERCÍCIO               R$   238.260,00\n\n"
        "Patrimônio Líquido: R$ 890.000,00\n"
        "Ativo Total: R$ 1.450.000,00\n"
        "Passivo Total: R$ 560.000,00\n",
        fontsize=10,
    )
    path = OUTPUT_DIR / "sample_financial_report.pdf"
    doc.save(str(path))
    doc.close()
    print(f"Created: {path}")


if __name__ == "__main__":
    print("Generating sample documents...")
    make_contract()
    make_invoice()
    make_financial_report()
    print("\nDone! Upload these files via http://localhost:8000 to try the pipeline.")
