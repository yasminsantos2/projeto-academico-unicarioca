"""Migration inicial: prepara a collection de produtos do estoque.

Cria a collection `produtos` e seus indices. O `_id` (ObjectId) e o
identificador nativo de cada produto, entao nao criamos id sequencial.
"""


def up(db):
    if 'produtos' not in db.list_collection_names():
        db.create_collection('produtos')

    produtos = db['produtos']

    produtos.create_index('status')
    produtos.create_index('categoria')
    produtos.create_index('nome')
    produtos.create_index(
        'codigo_barras',
        unique=True,
        partialFilterExpression={'codigo_barras': {'$type': 'string'}},
    )
