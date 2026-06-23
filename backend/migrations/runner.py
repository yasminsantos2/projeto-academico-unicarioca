import os
import importlib.util
from datetime import datetime

import pymongo

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/')
DB_NAME = os.environ.get('MONGO_DB', 'unicarioca')
MIGRATIONS_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_migrations():
    files = sorted(
        f for f in os.listdir(MIGRATIONS_DIR)
        if f[:3].isdigit() and f.endswith('.py')
    )
    migrations = []
    for fname in files:
        path = os.path.join(MIGRATIONS_DIR, fname)
        spec = importlib.util.spec_from_file_location(fname[:-3], path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        migrations.append((fname, module))
    return migrations


def run():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    control = db['_migrations']
    applied = {doc['name'] for doc in control.find({}, {'name': 1})}

    for name, module in _load_migrations():
        if name in applied:
            print(f'[skip] {name}')
            continue
        print(f'[run ] {name}')
        module.up(db)
        control.insert_one({'name': name, 'applied_at': datetime.utcnow()})
        print(f'[done] {name}')

    print('Migrations concluidas.')
