"""Enums do dominio, tipando os campos da entidade Produto.

Herdam de str para serializar direto em JSON e gravar como texto no Mongo.
"""

from enum import Enum


class Categoria(str, Enum):
    ALIMENTOS = 'alimentos'
    BEBIDAS = 'bebidas'
    LIMPEZA = 'limpeza'
    HIGIENE = 'higiene'
    PAPELARIA = 'papelaria'
    UTILIDADES = 'utilidades'
    OUTROS = 'outros'


class UnidadeMedida(str, Enum):
    UN = 'un'
    KG = 'kg'
    G = 'g'
    L = 'l'
    ML = 'ml'
    PCT = 'pct'
    CX = 'cx'


class SituacaoEstoque(str, Enum):
    OK = 'ok'
    BAIXO = 'baixo'
    ESGOTADO = 'esgotado'


class StatusProduto(str, Enum):
    ATIVO = 'ativo'
    DESCONTINUADO = 'descontinuado'
