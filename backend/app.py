from flask import Flask, jsonify, request
import pymongo

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "A API Flask está rodando!", "status": "Tudo está funcionando corretamente na porta 5000", "endpoints": ["/projects"]})

projects = []

@app.route('/projects', methods=['GET'])
def get_projects():
    return jsonify(projects)

@app.route('/projects', methods=['POST'])
def add_project():
    data = request.get_json() or {}
    project = {
        'id': len(projects) + 1,
        'name': data.get('name', 'Novo Projeto')
    }
    projects.append(project)
    return jsonify(project), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
