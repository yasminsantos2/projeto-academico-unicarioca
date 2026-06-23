"""Testes unitarios do ProdutoService usando um repositorio falso (DI).

Usa unittest da biblioteca padrao (sem dependencia externa).
"""

import unittest

from services.exceptions import ProdutoNaoEncontrado, ValidacaoError
from services.produto_service import ProdutoService
from tests.fake_repository import FakeProdutoRepository


def _dados_validos(**overrides):
    base = {
        'nome': 'Cafe 500g',
        'categoria': 'alimentos',
        'preco_unitario': 15.0,
        'quantidade_estoque': 10,
        'estoque_minimo': 3,
        'unidade_medida': 'pct',
    }
    base.update(overrides)
    return base


class TestProdutoService(unittest.TestCase):
    def setUp(self):
        self.service = ProdutoService(FakeProdutoRepository())

    # ---------- cadastrar ----------

    def test_cadastrar_produto_valido(self):
        produto = self.service.cadastrar(_dados_validos())
        self.assertIsNotNone(produto._id)
        self.assertEqual(produto.nome, 'Cafe 500g')

    def test_cadastrar_invalido_lanca_validacao(self):
        with self.assertRaises(ValidacaoError) as ctx:
            self.service.cadastrar({'nome': ''})
        self.assertIn('nome e obrigatorio', ctx.exception.erros)

    def test_cadastrar_categoria_invalida(self):
        with self.assertRaises(ValidacaoError) as ctx:
            self.service.cadastrar(_dados_validos(categoria='inexistente'))
        self.assertIn('categoria invalida', ctx.exception.erros)

    def test_cadastrar_codigo_barras_duplicado(self):
        self.service.cadastrar(_dados_validos(codigo_barras='999'))
        with self.assertRaises(ValidacaoError) as ctx:
            self.service.cadastrar(_dados_validos(nome='Outro', codigo_barras='999'))
        self.assertIn('codigo_barras ja cadastrado em outro produto', ctx.exception.erros)

    # ---------- buscar / atualizar ----------

    def test_buscar_por_id_inexistente(self):
        with self.assertRaises(ProdutoNaoEncontrado):
            self.service.buscar_por_id('6a39fe92c55dbce1e7990d31')

    def test_atualizar_produto_existente(self):
        produto = self.service.cadastrar(_dados_validos())
        atualizado = self.service.atualizar(produto._id, {'preco_unitario': 20.0})
        self.assertEqual(atualizado.preco_unitario, 20.0)

    def test_atualizar_inexistente_lanca_nao_encontrado(self):
        with self.assertRaises(ProdutoNaoEncontrado):
            self.service.atualizar('6a39fe92c55dbce1e7990d31', {'preco_unitario': 1})

    def test_atualizar_valor_invalido(self):
        produto = self.service.cadastrar(_dados_validos())
        with self.assertRaises(ValidacaoError):
            self.service.atualizar(produto._id, {'preco_unitario': -5})

    # ---------- ajuste rapido de quantidade ----------

    def test_ajustar_quantidade_valida(self):
        produto = self.service.cadastrar(_dados_validos())
        atualizado = self.service.ajustar_quantidade(produto._id, 99)
        self.assertEqual(atualizado.quantidade_estoque, 99)

    def test_ajustar_quantidade_negativa(self):
        produto = self.service.cadastrar(_dados_validos())
        with self.assertRaises(ValidacaoError):
            self.service.ajustar_quantidade(produto._id, -1)

    def test_ajustar_quantidade_nao_inteira(self):
        produto = self.service.cadastrar(_dados_validos())
        with self.assertRaises(ValidacaoError):
            self.service.ajustar_quantidade(produto._id, 2.5)

    # ---------- exclusao logica ----------

    def test_excluir_faz_soft_delete(self):
        produto = self.service.cadastrar(_dados_validos())
        resultado = self.service.excluir(produto._id)
        self.assertIn('excluido', resultado['mensagem'])
        with self.assertRaises(ProdutoNaoEncontrado):
            self.service.buscar_por_id(produto._id)

    # ---------- resumo ----------

    def test_gerar_resumo_conta_situacoes(self):
        self.service.cadastrar(_dados_validos(nome='OK', quantidade_estoque=10, estoque_minimo=2))
        self.service.cadastrar(_dados_validos(nome='Baixo', quantidade_estoque=2, estoque_minimo=5))
        self.service.cadastrar(_dados_validos(nome='Esgotado', quantidade_estoque=0, estoque_minimo=5))
        _, resumo = self.service.listar()
        self.assertEqual(resumo.total_produtos, 3)
        self.assertEqual(resumo.produtos_em_alerta, 1)
        self.assertEqual(resumo.produtos_esgotados, 1)

    # ---------- validacao parcial ----------

    def test_validacao_parcial_ignora_campos_ausentes(self):
        self.assertEqual(self.service.validar({'preco_unitario': 5}, parcial=True), [])

    def test_validacao_completa_exige_obrigatorios(self):
        erros = self.service.validar({}, parcial=False)
        self.assertIn('nome e obrigatorio', erros)
        self.assertIn('categoria e obrigatoria', erros)


if __name__ == '__main__':
    unittest.main()
