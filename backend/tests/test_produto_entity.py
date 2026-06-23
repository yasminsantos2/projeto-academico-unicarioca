"""Testes unitarios da entidade Produto (regra de situacao + mapeamento).

Usa unittest da biblioteca padrao (sem dependencia externa).
"""

import unittest
from datetime import datetime

from bson import ObjectId

from domain.enums import SituacaoEstoque
from domain.produto import Produto


def _produto(quantidade, minimo):
    return Produto(
        nome='Item',
        categoria='alimentos',
        preco_unitario=1.0,
        quantidade_estoque=quantidade,
        estoque_minimo=minimo,
    )


class TestProdutoEntity(unittest.TestCase):
    def test_situacao_esgotado_quando_quantidade_zero(self):
        self.assertEqual(_produto(0, 5).calcular_situacao(), SituacaoEstoque.ESGOTADO.value)

    def test_situacao_baixo_quando_igual_ao_minimo(self):
        self.assertEqual(_produto(5, 5).calcular_situacao(), SituacaoEstoque.BAIXO.value)

    def test_situacao_baixo_quando_abaixo_do_minimo(self):
        self.assertEqual(_produto(3, 5).calcular_situacao(), SituacaoEstoque.BAIXO.value)

    def test_situacao_ok_quando_acima_do_minimo(self):
        self.assertEqual(_produto(10, 5).calcular_situacao(), SituacaoEstoque.OK.value)

    def test_to_dict_inclui_situacao_e_id_string(self):
        produto = _produto(10, 5)
        produto._id = ObjectId()
        dados = produto.to_dict()
        self.assertEqual(dados['situacao'], SituacaoEstoque.OK.value)
        self.assertEqual(dados['id'], str(produto._id))
        self.assertIsInstance(dados['id'], str)

    def test_to_dict_id_none_quando_sem_id(self):
        self.assertIsNone(_produto(1, 1).to_dict()['id'])

    def test_to_document_nao_inclui_id(self):
        documento = _produto(1, 1).to_document()
        self.assertNotIn('_id', documento)
        self.assertEqual(documento['nome'], 'Item')

    def test_from_document_reconstroi_entidade(self):
        agora = datetime.utcnow()
        documento = {
            '_id': ObjectId(),
            'nome': 'Arroz',
            'categoria': 'alimentos',
            'descricao': 'pacote',
            'preco_unitario': 9.9,
            'quantidade_estoque': 4,
            'estoque_minimo': 2,
            'unidade_medida': 'pct',
            'codigo_barras': '123',
            'fornecedor': 'X',
            'status': 'ativo',
            'data_cadastro': agora,
            'data_ultima_atualizacao': agora,
            'data_exclusao': None,
        }
        produto = Produto.from_document(documento)
        self.assertEqual(produto.nome, 'Arroz')
        self.assertEqual(produto.quantidade_estoque, 4)
        self.assertEqual(produto._id, documento['_id'])
        self.assertEqual(produto.calcular_situacao(), SituacaoEstoque.OK.value)


if __name__ == '__main__':
    unittest.main()
