"""Live Neo4j integration checks. Run after importing the Movies graph."""
import getpass
import json
import os
from neo4j import GraphDatabase
from app import load_config, retrieve

config = load_config()
password = os.environ.get('NEO4J_PASSWORD') or getpass.getpass('Neo4j password: ')
checks = [
    ('director', 'The Matrix', 'director', {'Lana Wachowski', 'Lilly Wachowski'}),
    ('cast', 'The Matrix', 'actor', {'Keanu Reeves', 'Carrie-Anne Moss'}),
    ('actor_movies', 'Tom Hanks', 'movie', {'Apollo 13'}),
    ('director_movies', 'Nora Ephron', 'movie', {'Sleepless in Seattle'}),
    ('movie', 'The Matrix', 'year', {1999}),
]
with GraphDatabase.driver(config['neo4j_uri'], auth=(config['neo4j_user'], password)) as driver:
    driver.verify_connectivity()
    for intent, entity, field, expected in checks:
        rows, _ = retrieve(driver, config['neo4j_database'], intent, entity, 50)
        actual = {r[field] for r in rows}
        if not expected <= actual:
            raise AssertionError(f'{intent}: expected {expected}, received {actual}')
        print(f'PASS {intent}: {json.dumps(rows)}')
    rows, _ = retrieve(driver, config['neo4j_database'], 'recommend', 'The Matrix', 5)
    assert rows and all(r['movie'] != 'The Matrix' and r['score'] > 0 for r in rows)
    assert all(r['score'] == len(r['shared_actors']) for r in rows)
    print('PASS recommendations: ' + json.dumps(rows))
    rows, _ = retrieve(driver, config['neo4j_database'], 'movie', '__missing_movie__')
    assert not rows
    print('PASS missing entity')
