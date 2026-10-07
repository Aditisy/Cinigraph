"""Run against the actual website; save all evidence and generated answers."""
import json
from pathlib import Path
import time
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
cases=[
    ('Who directed The Matrix?', 'director', 'Lana Wachowski'),
    ('Who acted in The Matrix?', 'cast', 'Keanu Reeves'),
    ('Movies with Tom Hanks', 'actor_movies', 'Apollo 13'),
    ('Movies directed by Nora Ephron', 'director_movies', 'Sleepless in Seattle'),
    ('When was The Matrix released?', 'movie', '1999'),
    ('Recommend movies like The Matrix', 'recommend', 'The Matrix Reloaded'),
    ('Tell me about __missing_movie__', 'movie', None),
]
results=[]
for question,intent,expected in cases:
    req=urllib.request.Request('http://127.0.0.1:8765/api/ask',
        data=json.dumps({'question':question}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=240) as response:
        result=json.load(response)
    assert result['intent']==intent
    assert 'generation_error' not in result,result
    if expected:
        assert expected in json.dumps(result['evidence']),result
        assert result['answer'].strip()
    else:
        assert not result['evidence']
        assert 'No matching evidence' in result['answer']
    results.append(result)
    print('PASS',question,result['elapsed_seconds'],'seconds',flush=True)
req=urllib.request.Request('http://127.0.0.1:8765/api/ask',
    data=json.dumps({'question':'Who won an Oscar?'}).encode(),headers={'Content-Type':'application/json'})
try:
    urllib.request.urlopen(req)
    raise AssertionError('Unsupported question should fail')
except urllib.error.HTTPError as e:
    assert e.code==400
    results.append({'question':'Who won an Oscar?','status':400,'response':json.load(e)})
(ROOT/'output'/'live_results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('8 live acceptance cases passed. Inspect answer claims manually; these checks do not score groundedness.')
