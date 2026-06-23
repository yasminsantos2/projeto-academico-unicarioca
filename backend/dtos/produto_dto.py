"""DTOs de Produto: traducao entre o mundo HTTP (JSON) e o dominio.

- from_request: filtra apenas os campos aceitos do payload (evita que o
  cliente injete campos como _id, datas ou data_exclusao).
- to_response / lista_to_response: formatam a saida da API.
A validacao de regras NAO acontece aqui (e responsabilidade do service).
"""

from typing import List

from domain.produto import Produto, ResumoEstoque

CAMPOS_ENTRADA = [
    'nome', 'categoria', 'descricao', 'preco_unitario', 'quantidade_estoque',
    'estoque_minimo', 'unidade_medida', 'codigo_barras', 'fornecedor', 'status',
]


class ProdutoDTO:
    @staticmethod
    def from_request(payload: dict) -> dict:
        payload = payload or {}
        return {campo: payload[campo] for campo in CAMPOS_ENTRADA if campo in payload}

    @staticmethod
    def to_response(produto: Produto) -> dict:
        return produto.to_dict()

    @staticmethod
    def lista_to_response(produtos: List[Produto], resumo: ResumoEstoque) -> dict:
        return {
            'produtos': [p.to_dict() for p in produtos],
            'resumo': resumo.to_dict(),
        }
