"""Camada de servico: concentra as regras de negocio de Produto.

Injecao de dependencia: o repositorio e recebido no construtor, entao o
service nao conhece detalhes do MongoDB e pode ser testado com um repositorio
falso. As regras (validacao, situacao, resumo, exclusao logica) vivem aqui,
nunca no controller nem no repositorio.
"""

from typing import List, Optional, Tuple

from pymongo.errors import DuplicateKeyError

from domain.enums import Categoria, SituacaoEstoque, StatusProduto, UnidadeMedida
from domain.produto import Produto, ResumoEstoque
from repositories.produto_repository import ProdutoRepository

from .exceptions import ProdutoNaoEncontrado, ValidacaoError

CAMPOS_ATUALIZAVEIS = [
    'nome', 'categoria', 'descricao', 'preco_unitario', 'quantidade_estoque',
    'estoque_minimo', 'unidade_medida', 'codigo_barras', 'fornecedor', 'status',
]


class ProdutoService:
    def __init__(self, repository: ProdutoRepository):
        self.repository = repository

    # ---------- casos de uso ----------

    def listar(self, filtros: Optional[dict] = None) -> Tuple[List[Produto], ResumoEstoque]:
        produtos = self.repository.find_all(filtros)
        return produtos, self.gerar_resumo(produtos)

    def buscar_por_id(self, produto_id) -> Produto:
        produto = self.repository.find_by_id(produto_id)
        if produto is None:
            raise ProdutoNaoEncontrado(produto_id)
        return produto

    def cadastrar(self, dados: dict) -> Produto:
        erros = self.validar(dados)
        if erros:
            raise ValidacaoError(erros)
        produto = self._montar_produto(dados)
        try:
            return self.repository.insert(produto)
        except DuplicateKeyError:
            raise ValidacaoError(['codigo_barras ja cadastrado em outro produto'])

    def atualizar(self, produto_id, dados: dict) -> Produto:
        self.buscar_por_id(produto_id)
        erros = self.validar(dados, parcial=True)
        if erros:
            raise ValidacaoError(erros)
        campos = self._campos_atualizaveis(dados)
        if not campos:
            raise ValidacaoError(['nenhum campo valido para atualizar'])
        try:
            return self.repository.update(produto_id, campos)
        except DuplicateKeyError:
            raise ValidacaoError(['codigo_barras ja cadastrado em outro produto'])

    def ajustar_quantidade(self, produto_id, nova_quantidade) -> Produto:
        """Ajuste rapido de quantidade (caso de uso «extend»)."""
        self.buscar_por_id(produto_id)
        if not self._eh_inteiro(nova_quantidade):
            raise ValidacaoError(['quantidade_estoque deve ser um numero inteiro'])
        if nova_quantidade < 0:
            raise ValidacaoError(['quantidade_estoque nao pode ser negativo'])
        return self.repository.update(produto_id, {'quantidade_estoque': int(nova_quantidade)})

    def excluir(self, produto_id) -> dict:
        self.buscar_por_id(produto_id)
        self.repository.soft_delete(produto_id)
        return {'id': str(produto_id), 'mensagem': 'Produto excluido com sucesso'}

    # ---------- regras de negocio ----------

    def gerar_resumo(self, produtos: List[Produto]) -> ResumoEstoque:
        resumo = ResumoEstoque(total_produtos=len(produtos))
        for produto in produtos:
            situacao = produto.calcular_situacao()
            if situacao == SituacaoEstoque.ESGOTADO.value:
                resumo.produtos_esgotados += 1
            elif situacao == SituacaoEstoque.BAIXO.value:
                resumo.produtos_em_alerta += 1
        return resumo

    def validar(self, dados: dict, parcial: bool = False) -> list:
        """Valida os dados. Em modo parcial (update) so checa o que foi enviado."""
        erros: List[str] = []
        dados = dados or {}

        def ausente(campo):
            return campo not in dados or dados.get(campo) in (None, '')

        if not parcial or 'nome' in dados:
            if ausente('nome'):
                erros.append('nome e obrigatorio')
            elif not isinstance(dados['nome'], str):
                erros.append('nome deve ser texto')

        if not parcial or 'categoria' in dados:
            if ausente('categoria'):
                erros.append('categoria e obrigatoria')
            elif dados['categoria'] not in [c.value for c in Categoria]:
                erros.append('categoria invalida')

        if not parcial or 'preco_unitario' in dados:
            erros += self._validar_numero(dados, 'preco_unitario', ausente, inteiro=False)
        if not parcial or 'quantidade_estoque' in dados:
            erros += self._validar_numero(dados, 'quantidade_estoque', ausente, inteiro=True)
        if not parcial or 'estoque_minimo' in dados:
            erros += self._validar_numero(dados, 'estoque_minimo', ausente, inteiro=True)

        if dados.get('unidade_medida') and dados['unidade_medida'] not in [u.value for u in UnidadeMedida]:
            erros.append('unidade_medida invalida')
        if dados.get('status') and dados['status'] not in [s.value for s in StatusProduto]:
            erros.append('status invalido')

        return erros

    # ---------- helpers internos ----------

    def _montar_produto(self, dados: dict) -> Produto:
        return Produto(
            nome=dados['nome'].strip(),
            categoria=dados['categoria'],
            descricao=(dados.get('descricao') or '').strip(),
            preco_unitario=float(dados['preco_unitario']),
            quantidade_estoque=int(dados['quantidade_estoque']),
            estoque_minimo=int(dados['estoque_minimo']),
            unidade_medida=dados.get('unidade_medida') or UnidadeMedida.UN.value,
            codigo_barras=dados.get('codigo_barras') or None,
            fornecedor=dados.get('fornecedor') or None,
            status=dados.get('status') or StatusProduto.ATIVO.value,
        )

    def _campos_atualizaveis(self, dados: dict) -> dict:
        campos = {c: dados[c] for c in CAMPOS_ATUALIZAVEIS if c in dados}
        for campo in ('preco_unitario',):
            if campo in campos:
                campos[campo] = float(campos[campo])
        for campo in ('quantidade_estoque', 'estoque_minimo'):
            if campo in campos:
                campos[campo] = int(campos[campo])
        if 'nome' in campos and isinstance(campos['nome'], str):
            campos['nome'] = campos['nome'].strip()
        return campos

    @staticmethod
    def _eh_inteiro(valor) -> bool:
        if isinstance(valor, bool):
            return False
        return isinstance(valor, int) or (isinstance(valor, float) and valor.is_integer())

    @classmethod
    def _validar_numero(cls, dados, campo, ausente, inteiro) -> list:
        if ausente(campo):
            return [f'{campo} e obrigatorio']
        valor = dados[campo]
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            return [f'{campo} deve ser numerico']
        if inteiro and not float(valor).is_integer():
            return [f'{campo} deve ser inteiro']
        if valor < 0:
            return [f'{campo} nao pode ser negativo']
        return []
