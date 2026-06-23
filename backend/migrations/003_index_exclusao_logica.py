"""Indices para a exclusao logica, alinhando o banco ao repositorio.

O ProdutoRepository filtra `data_exclusao: None` em todas as buscas e a
listagem padrao ordena por nome. Estes indices tornam esse caminho eficiente:
  - data_exclusao: filtro presente em toda query
  - (data_exclusao, nome): listagem de ativos ordenada por nome
"""


def up(db):
    produtos = db['produtos']

    produtos.create_index('data_exclusao')
    produtos.create_index([('data_exclusao', 1), ('nome', 1)])
