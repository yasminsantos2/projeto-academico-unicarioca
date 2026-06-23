"""Repositorio de Produto: isola todo o acesso ao MongoDB.

Converte entre entidade Produto e documentos Mongo via Produto.from_document /
to_document. A exclusao logica e feita marcando data_exclusao (mantem historico),
entao todas as buscas ignoram produtos ja excluidos.
"""

from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId

from domain.produto import Produto


class ProdutoRepository:
    def __init__(self, db):
        self.collection = db['produtos']

    @staticmethod
    def _to_object_id(produto_id) -> Optional[ObjectId]:
        try:
            return ObjectId(produto_id)
        except (InvalidId, TypeError):
            return None

    def find_all(self, filtros: Optional[dict] = None) -> List[Produto]:
        query = {'data_exclusao': None}
        filtros = filtros or {}

        if filtros.get('categoria'):
            query['categoria'] = filtros['categoria']
        if filtros.get('status'):
            query['status'] = filtros['status']
        if filtros.get('busca'):
            query['nome'] = {'$regex': filtros['busca'], '$options': 'i'}

        docs = self.collection.find(query).sort('nome', 1)
        return [Produto.from_document(doc) for doc in docs]

    def find_by_id(self, produto_id) -> Optional[Produto]:
        oid = self._to_object_id(produto_id)
        if oid is None:
            return None
        doc = self.collection.find_one({'_id': oid, 'data_exclusao': None})
        return Produto.from_document(doc) if doc else None

    def insert(self, produto: Produto) -> Produto:
        agora = datetime.utcnow()
        produto.data_cadastro = agora
        produto.data_ultima_atualizacao = agora
        produto.data_exclusao = None
        resultado = self.collection.insert_one(produto.to_document())
        produto._id = resultado.inserted_id
        return produto

    def update(self, produto_id, dados: dict) -> Optional[Produto]:
        oid = self._to_object_id(produto_id)
        if oid is None:
            return None
        dados = dict(dados)
        dados['data_ultima_atualizacao'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': oid, 'data_exclusao': None},
            {'$set': dados},
        )
        return self.find_by_id(produto_id)

    def soft_delete(self, produto_id) -> bool:
        oid = self._to_object_id(produto_id)
        if oid is None:
            return False
        agora = datetime.utcnow()
        resultado = self.collection.update_one(
            {'_id': oid, 'data_exclusao': None},
            {'$set': {'data_exclusao': agora, 'data_ultima_atualizacao': agora}},
        )
        return resultado.modified_count > 0
