"""Controller HTTP de Produto (Flask Blueprint).

Injecao de dependencia: o service e recebido por parametro na factory
`criar_produto_controller`, entao o controller nao instancia nada - apenas
traduz requisicao/resposta HTTP e delega as regras ao service.
"""

from flask import Blueprint, jsonify, request

from dtos.produto_dto import ProdutoDTO
from services.produto_service import ProdutoService


def criar_produto_controller(service: ProdutoService) -> Blueprint:
    bp = Blueprint('produtos', __name__, url_prefix='/produtos')

    @bp.route('', methods=['GET'])
    def listar():
        filtros = {
            'categoria': request.args.get('categoria'),
            'status': request.args.get('status'),
            'busca': request.args.get('busca'),
        }
        produtos, resumo = service.listar(filtros)
        return jsonify(ProdutoDTO.lista_to_response(produtos, resumo)), 200

    @bp.route('/<produto_id>', methods=['GET'])
    def detalhar(produto_id):
        produto = service.buscar_por_id(produto_id)
        return jsonify(ProdutoDTO.to_response(produto)), 200

    @bp.route('', methods=['POST'])
    def cadastrar():
        dados = ProdutoDTO.from_request(request.get_json(silent=True))
        produto = service.cadastrar(dados)
        return jsonify(ProdutoDTO.to_response(produto)), 201

    @bp.route('/<produto_id>', methods=['PUT'])
    def atualizar(produto_id):
        dados = ProdutoDTO.from_request(request.get_json(silent=True))
        produto = service.atualizar(produto_id, dados)
        return jsonify(ProdutoDTO.to_response(produto)), 200

    @bp.route('/<produto_id>/quantidade', methods=['PATCH'])
    def ajustar_quantidade(produto_id):
        payload = request.get_json(silent=True) or {}
        produto = service.ajustar_quantidade(produto_id, payload.get('quantidade_estoque'))
        return jsonify(ProdutoDTO.to_response(produto)), 200

    @bp.route('/<produto_id>', methods=['DELETE'])
    def excluir(produto_id):
        resultado = service.excluir(produto_id)
        return jsonify(resultado), 200

    return bp
