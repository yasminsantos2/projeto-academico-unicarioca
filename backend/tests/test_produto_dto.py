"""Testes unitarios do ProdutoDTO (traducao HTTP <-> dominio).

Usa unittest da biblioteca padrao (sem dependencia externa).
"""

import unittest

from bson import ObjectId

from domain.produto import Produto, ResumoEstoque
from dtos.produto_dto import ProdutoDTO


class TestProdutoDTO(unittest.TestCase):
    def test_from_request_filtra_campos_desconhecidos(self):
        payload = {
            'nome': 'Item',
            'categoria': 'alimentos',
            '_id': 'hack',
            'data_exclusao': '2020-01-01',
            'situacao': 'ok',
        }
        dados = ProdutoDTO.from_request(payload)
        self.assertEqual(dados, {'nome': 'Item', 'categoria': 'alimentos'})
        self.assertNotIn('_id', dados)
        self.assertNotIn('data_exclusao', dados)

    def test_from_request_none_retorna_vazio(self):
        self.assertEqual(ProdutoDTO.from_request(None), {})

    def test_to_response_usa_to_dict(self):
        produto = Produto(
            nome='Item', categoria='alimentos', preco_unitario=1.0,
            quantidade_estoque=10, estoque_minimo=5,
        )
        produto._id = ObjectId()
        resposta = ProdutoDTO.to_response(produto)
        self.assertEqual(resposta['nome'], 'Item')
        self.assertEqual(resposta['situacao'], 'ok')

    def test_lista_to_response_inclui_produtos_e_resumo(self):
        produto = Produto(
            nome='Item', categoria='alimentos', preco_unitario=1.0,
            quantidade_estoque=10, estoque_minimo=5,
        )
        resumo = ResumoEstoque(total_produtos=1)
        resposta = ProdutoDTO.lista_to_response([produto], resumo)
        self.assertIn('produtos', resposta)
        self.assertIn('resumo', resposta)
        self.assertEqual(len(resposta['produtos']), 1)
        self.assertEqual(resposta['resumo']['total_produtos'], 1)


if __name__ == '__main__':
    unittest.main()
