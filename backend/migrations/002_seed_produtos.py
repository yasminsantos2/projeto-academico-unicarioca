"""Seed de produtos de exemplo para o estoque.

Insere 3 produtos cobrindo as situacoes possiveis (ok, baixo, esgotado),
de acordo com a comparacao entre quantidade_estoque e estoque_minimo.
So insere se a collection estiver vazia, para nao duplicar dados.
"""

from datetime import datetime


def up(db):
    produtos = db['produtos']

    if produtos.count_documents({}) > 0:
        return

    agora = datetime.utcnow()

    produtos.insert_many([
        {
            'nome': 'Arroz Branco 5kg',
            'categoria': 'alimentos',
            'descricao': 'Arroz tipo 1, pacote de 5kg',
            'preco_unitario': 28.90,
            'quantidade_estoque': 40,
            'estoque_minimo': 10,
            'unidade_medida': 'pct',
            'codigo_barras': '7891000100101',
            'fornecedor': 'Distribuidora Central',
            'status': 'ativo',
            'data_cadastro': agora,
            'data_ultima_atualizacao': agora,
            'data_exclusao': None,
        },
        {
            'nome': 'Caneta Esferografica Azul',
            'categoria': 'papelaria',
            'descricao': 'Caneta azul, caixa unitaria',
            'preco_unitario': 1.50,
            'quantidade_estoque': 8,
            'estoque_minimo': 20,
            'unidade_medida': 'un',
            'codigo_barras': '7891000200202',
            'fornecedor': 'Papelaria Mundial',
            'status': 'ativo',
            'data_cadastro': agora,
            'data_ultima_atualizacao': agora,
            'data_exclusao': None,
        },
        {
            'nome': 'Refrigerante Cola 2L',
            'categoria': 'bebidas',
            'descricao': 'Refrigerante sabor cola, garrafa 2 litros',
            'preco_unitario': 9.90,
            'quantidade_estoque': 0,
            'estoque_minimo': 12,
            'unidade_medida': 'un',
            'codigo_barras': '7891000300303',
            'fornecedor': 'Bebidas Express',
            'status': 'ativo',
            'data_cadastro': agora,
            'data_ultima_atualizacao': agora,
            'data_exclusao': None,
        },
    ])
