"""Loopback-only web interface for the movie Graph RAG lab."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.runtime' / 'python'))
import json
import os
import time
import urllib.request
from flask import Flask, jsonify, request, send_from_directory
from neo4j import GraphDatabase
from app import load_config, answer_question

app = Flask(__name__, static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 8192
config = load_config()
password_file = ROOT / '.runtime' / 'password.txt'
password = os.environ.get('NEO4J_PASSWORD') or (password_file.read_text().strip() if password_file.exists() else '')
driver = GraphDatabase.driver(config['neo4j_uri'], auth=(config['neo4j_user'], password), connection_timeout=10)

def query(cypher, **params):
    records, _, _ = driver.execute_query(cypher, parameters_=params,
                                        database_=config['neo4j_database'], routing_='r')
    return [r.data() for r in records]

@app.get('/')
def index():
    return send_from_directory('static', 'index.html')

@app.get('/api/status')
def status():
    result = {'database': False, 'llm': False, 'model': config.get('model_label',config['ollama_model'])}
    try:
        result.update(query('MATCH (m:Movie) WITH count(m) AS movies MATCH (p:Person) '
                            'WITH movies, count(p) AS people MATCH ()-[r]->() '
                            'RETURN movies, people, count(r) AS relationships')[0])
        result['database'] = True
    except Exception:
        pass
    try:
        with urllib.request.urlopen(config.get('llama_url','http://127.0.0.1:8081')+'/health',timeout=3) as r:
            result['llm'] = r.status == 200
    except Exception:
        pass
    return jsonify(result)

@app.get('/api/movies')
def movies():
    return jsonify(query('MATCH (m:Movie) OPTIONAL MATCH (p:Person)-[:ACTED_IN]->(m) '
                         'RETURN m.title AS title,m.released AS year,m.tagline AS tagline, '
                         'count(p) AS cast_count ORDER BY title'))

@app.get('/api/graph')
def graph():
    title=request.args.get('title','The Matrix')
    rows=query('MATCH (m:Movie) WHERE m.title=$title OPTIONAL MATCH (p:Person)-[r:ACTED_IN|DIRECTED]->(m) '
               'RETURN m.title AS movie,p.name AS person,type(r) AS relation ORDER BY person',title=title)
    return jsonify(rows)

@app.post('/api/ask')
def ask():
    origin=request.headers.get('Origin')
    if origin and origin not in ('http://127.0.0.1:8765','http://localhost:8765'):
        return jsonify(error='Origin not allowed.'),403
    body=request.get_json(silent=True) or {}
    if not isinstance(body,dict):
        return jsonify(error='Request body must be a JSON object.'),400
    question=body.get('question','')
    if not isinstance(question,str):
        return jsonify(error='Question must be text.'),400
    start=time.perf_counter()
    try:
        result=answer_question(driver,config,question,limit=10)
        result['elapsed_seconds']=round(time.perf_counter()-start,2)
        result['model']=config.get('model_label',config['ollama_model'])
        return jsonify(result)
    except ValueError as exc:
        return jsonify(error=str(exc)),400
    except Exception:
        return jsonify(error='The movie database is unavailable. Start the local services and retry.'),503

@app.get('/report.pdf')
def report():
    return send_from_directory(ROOT/'output'/'pdf','Exercise_3_Report.pdf')

if __name__=='__main__':
    app.run(host='127.0.0.1',port=8765,debug=False,threaded=True)
