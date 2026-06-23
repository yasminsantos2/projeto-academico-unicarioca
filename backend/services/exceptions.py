"""Excecoes de negocio.

Permitem que o service sinalize falhas sem conhecer HTTP; o controller
traduz cada uma para o status code adequado (400 / 404).
"""


class ServiceError(Exception):
    pass


class ValidacaoError(ServiceError):
    def __init__(self, erros):
        self.erros = erros if isinstance(erros, list) else [erros]
        super().__init__('; '.join(self.erros))


class ProdutoNaoEncontrado(ServiceError):
    def __init__(self, produto_id):
        self.produto_id = produto_id
        super().__init__(f'Produto nao encontrado: {produto_id}')
