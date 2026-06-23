"""Repositorio falso em memoria para testar o service sem MongoDB.

Implementa a mesma interface do ProdutoRepository. Graças à injecao de
dependencia, o service nao percebe a diferenca.
"""

from datetime import datetime

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from domain.produto import Produto


class FakeProdutoRepository:
    def __init__(self):
        self._dados = {}

    def find_all(self, filtros=None):
        return [p for p in self._dados.values() if p.data_exclusao is None]

    def find_by_id(self, produto_id):
        produto = self._dados.get(str(produto_id))
        if produto is not None and produto.data_exclusao is None:
            return produto
        return None

    def insert(self, produto: Produto):
        if produto.codigo_barras:
            for existente in self._dados.values():
                if existente.codigo_barras == produto.codigo_barras:
                    raise DuplicateKeyError('codigo_barras duplicado')
        agora = datetime.utcnow()
        produto._id = ObjectId()
        produto.data_cadastro = agora
        produto.data_ultima_atualizacao = agora
        produto.data_exclusao = None
        self._dados[str(produto._id)] = produto
        return produto

    def update(self, produto_id, dados: dict):
        produto = self.find_by_id(produto_id)
        if produto is None:
            return None
        for campo, valor in dados.items():
            setattr(produto, campo, valor)
        return produto

    def soft_delete(self, produto_id):
        produto = self.find_by_id(produto_id)
        if produto is None:
            return False
        produto.data_exclusao = datetime.utcnow()
        return True
