"""Initialize only this project's private, local Neo4j instance."""
import os
from pathlib import Path
import time
from neo4j import GraphDatabase
ROOT=Path(__file__).resolve().parent
with GraphDatabase.driver('bolt://127.0.0.1:7689',auth=('neo4j',os.environ['NEO4J_PASSWORD'])) as driver:
    for attempt in range(45):
        try:
            driver.verify_connectivity()
            break
        except Exception:
            if attempt==44:
                raise
            time.sleep(2)
    records,_,_=driver.execute_query('MATCH (m:Movie) RETURN count(m) AS n',database_='neo4j')
    if not records[0]['n']:
        script=(ROOT/'data'/'movies.cypher').read_text(encoding='utf-8')
        # The official script has standalone constraints followed by one MERGE statement.
        for statement in script.split(';'):
            if statement.strip():
                driver.execute_query(statement,database_='neo4j')
        print('Official Movies graph loaded.')
    records,_,_=driver.execute_query('MATCH (m:Movie) RETURN count(m) AS movies',database_='neo4j')
    print(dict(records[0]))
