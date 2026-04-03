from flask import Flask, jsonify, request
import pymongo

app = Flask(__name__)

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
