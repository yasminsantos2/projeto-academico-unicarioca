"""Entidade de dominio Produto e o value object ResumoEstoque.

A entidade concentra a regra de negocio central (calcular_situacao) e o
mapeamento objeto <-> documento Mongo (to_document / from_document), que e a
camada de ORM/ODM deste projeto.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from .enums import SituacaoEstoque, StatusProduto, UnidadeMedida


@dataclass
class ResumoEstoque:
    total_produtos: int = 0
    produtos_em_alerta: int = 0
    produtos_esgotados: int = 0

    def to_dict(self) -> dict:
        return {
            'total_produtos': self.total_produtos,
            'produtos_em_alerta': self.produtos_em_alerta,
            'produtos_esgotados': self.produtos_esgotados,
        }


@dataclass
class Produto:
    nome: str
    categoria: str
    preco_unitario: float
    quantidade_estoque: int
    estoque_minimo: int
    unidade_medida: str = UnidadeMedida.UN.value
    descricao: str = ''
    codigo_barras: Optional[str] = None
    fornecedor: Optional[str] = None
    status: str = StatusProduto.ATIVO.value
    data_cadastro: Optional[datetime] = None
    data_ultima_atualizacao: Optional[datetime] = None
    data_exclusao: Optional[datetime] = None
    _id: Optional[ObjectId] = None

    def calcular_situacao(self) -> str:
        if self.quantidade_estoque <= 0:
            return SituacaoEstoque.ESGOTADO.value
        if self.quantidade_estoque <= self.estoque_minimo:
            return SituacaoEstoque.BAIXO.value
        return SituacaoEstoque.OK.value

    def to_dict(self) -> dict:
        """Representacao para a API (inclui id como string e a situacao calculada)."""
        return {
            'id': str(self._id) if self._id else None,
            'nome': self.nome,
            'categoria': self.categoria,
            'descricao': self.descricao,
            'preco_unitario': self.preco_unitario,
            'quantidade_estoque': self.quantidade_estoque,
            'estoque_minimo': self.estoque_minimo,
            'unidade_medida': self.unidade_medida,
            'codigo_barras': self.codigo_barras,
            'fornecedor': self.fornecedor,
            'status': self.status,
            'situacao': self.calcular_situacao(),
            'data_cadastro': self._iso(self.data_cadastro),
            'data_ultima_atualizacao': self._iso(self.data_ultima_atualizacao),
        }

    def to_document(self) -> dict:
        """Representacao para persistir no Mongo (sem _id; o Mongo gera/gerencia)."""
        return {
            'nome': self.nome,
            'categoria': self.categoria,
            'descricao': self.descricao,
            'preco_unitario': self.preco_unitario,
            'quantidade_estoque': self.quantidade_estoque,
            'estoque_minimo': self.estoque_minimo,
            'unidade_medida': self.unidade_medida,
            'codigo_barras': self.codigo_barras,
            'fornecedor': self.fornecedor,
            'status': self.status,
            'data_cadastro': self.data_cadastro,
            'data_ultima_atualizacao': self.data_ultima_atualizacao,
            'data_exclusao': self.data_exclusao,
        }

    @classmethod
    def from_document(cls, doc: dict) -> 'Produto':
        """Reconstroi a entidade a partir de um documento Mongo."""
        return cls(
            _id=doc.get('_id'),
            nome=doc.get('nome'),
            categoria=doc.get('categoria'),
            descricao=doc.get('descricao', ''),
            preco_unitario=doc.get('preco_unitario'),
            quantidade_estoque=doc.get('quantidade_estoque'),
            estoque_minimo=doc.get('estoque_minimo'),
            unidade_medida=doc.get('unidade_medida', UnidadeMedida.UN.value),
            codigo_barras=doc.get('codigo_barras'),
            fornecedor=doc.get('fornecedor'),
            status=doc.get('status', StatusProduto.ATIVO.value),
            data_cadastro=doc.get('data_cadastro'),
            data_ultima_atualizacao=doc.get('data_ultima_atualizacao'),
            data_exclusao=doc.get('data_exclusao'),
        )

    @staticmethod
    def _iso(value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None
