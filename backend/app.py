import os
from flask import Flask, jsonify, request
import pymongo

app = Flask(__name__)

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/')
client = pymongo.MongoClient(MONGO_URI)
db = client['unicarioca']
projects_collection = db['projects']

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "A API Flask está rodando!", "status": "Tudo está funcionando corretamente na porta 5000", "endpoints": ["/projects"]})

@app.route('/projects', methods=['GET'])
def get_projects():
    projects = list(projects_collection.find({}, {'_id': 0}))
    return jsonify(projects)

@app.route('/projects', methods=['POST'])
def add_project():
    data = request.get_json() or {}
    project = {
        'id': projects_collection.count_documents({}) + 1,
        'name': data.get('name', 'Novo Projeto')
    }
    projects_collection.insert_one(project)
    project.pop('_id', None)
    return jsonify(project), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
