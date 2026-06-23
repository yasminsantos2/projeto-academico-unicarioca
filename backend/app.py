"""Composition root da API de Controle de Estoque.

Aqui as dependencias sao montadas e injetadas em ordem:
    db -> ProdutoRepository -> ProdutoService -> ProdutoController (Blueprint)
Os erros de negocio do service sao traduzidos para status HTTP.
"""

import os

from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient

from controllers.produto_controller import criar_produto_controller
from repositories.produto_repository import ProdutoRepository
from services.exceptions import ProdutoNaoEncontrado, ValidacaoError
from services.produto_service import ProdutoService

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/')
MONGO_DB = os.environ.get('MONGO_DB', 'unicarioca')


def criar_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    db = MongoClient(MONGO_URI)[MONGO_DB]

    repository = ProdutoRepository(db)
    service = ProdutoService(repository)
    app.register_blueprint(criar_produto_controller(service))

    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'message': 'API de Controle de Estoque',
            'status': 'ok',
            'endpoints': ['/produtos'],
        })

    @app.errorhandler(ValidacaoError)
    def _erro_validacao(err):
        return jsonify({'erro': 'validacao', 'detalhes': err.erros}), 400

    @app.errorhandler(ProdutoNaoEncontrado)
    def _erro_nao_encontrado(err):
        return jsonify({'erro': 'nao_encontrado', 'mensagem': str(err)}), 404

    return app


app = criar_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
