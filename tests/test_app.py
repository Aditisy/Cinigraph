import json
import unittest
from unittest.mock import MagicMock, patch
import app


class PipelineTests(unittest.TestCase):
    def test_supported_questions(self):
        cases = [
            ('Who directed The Matrix?', ('director', 'The Matrix')),
            ('Who acted in "The Matrix"?', ('cast', 'The Matrix')),
            ('Movies with Tom Hanks', ('actor_movies', 'Tom Hanks')),
            ('Movies directed by Nora Ephron', ('director_movies', 'Nora Ephron')),
            ('When was The Matrix released?', ('movie', 'The Matrix')),
            ('Tell me about Apollo 13', ('movie', 'Apollo 13')),
            ('Recommend movies like The Matrix', ('recommend', 'The Matrix')),
            ('What movies did Tom Hanks act in?', ('actor_movies', 'Tom Hanks')),
        ]
        for question, expected in cases:
            with self.subTest(question=question):
                self.assertEqual(app.parse_question(question), expected)

    def test_unsupported_and_empty(self):
        for question in ['', 'Who won an Oscar?', 'x' * 501, 'Who directed   ?']:
            with self.subTest(question=question), self.assertRaises(ValueError):
                app.parse_question(question)

    def test_parameterization_and_read_routing(self):
        driver = MagicMock()
        driver.execute_query.return_value = ([], None, None)
        entity = "X' MATCH (n) DETACH DELETE n //"
        app.retrieve(driver, 'neo4j', 'movie', entity)
        args, kwargs = driver.execute_query.call_args
        self.assertNotIn(entity, args[0])
        self.assertEqual(kwargs['parameters_']['entity'], entity)
        self.assertEqual(kwargs['routing_'], 'r')

    def test_no_evidence_skips_llm(self):
        with patch('app.urllib.request.urlopen') as api:
            self.assertIn('No matching evidence', app.generate('question', [], {}))
            api.assert_not_called()

    def test_truncation(self):
        driver = MagicMock()
        driver.execute_query.return_value = ([MagicMock(data=lambda: {'movie': 'A'})] * 3, None, None)
        rows, partial = app.retrieve(driver, 'neo4j', 'movie', 'A', 2)
        self.assertEqual(len(rows), 2)
        self.assertTrue(partial)

    def test_llm_request_contains_evidence(self):
        response = MagicMock()
        response.read.return_value = b'{"response":"The Matrix was released in 1999 [R1]."}'
        response.__enter__.return_value = response
        with patch('app.urllib.request.urlopen', return_value=response) as api:
            answer = app.generate('When was The Matrix released?', [{'year': 1999}],
                                  {'ollama_url': 'http://localhost:11434', 'ollama_model': 'test'})
        self.assertIn('[R1]', answer)
        body = json.loads(api.call_args.args[0].data)
        self.assertEqual(json.loads(body['prompt'])['graph_evidence'][0]['year'], 1999)
        self.assertFalse(body['stream'])

    def test_failure_preserves_evidence(self):
        with patch('app.retrieve', return_value=([{'year': 1999}], False)), \
             patch('app.generate', side_effect=TimeoutError):
            result = app.answer_question(None, {'neo4j_database': 'neo4j'}, 'Tell me about The Matrix')
        self.assertEqual(result['evidence'][0]['year'], 1999)
        self.assertEqual(result['generation_error'], 'TimeoutError')

    def test_llama_chat_api_uses_server_template(self):
        response = MagicMock()
        response.read.return_value = b'{"choices":[{"message":{"content":"Released in 1999 [R1]."}}]}'
        response.__enter__.return_value = response
        config = {'ollama_url':'http://localhost:11434','ollama_model':'unused',
                  'llm_backend':'llama.cpp','llama_url':'http://127.0.0.1:8081'}
        with patch('app.urllib.request.urlopen',return_value=response) as api:
            answer=app.generate('When was The Matrix released?',[{'year':1999}],config)
        req=api.call_args.args[0]
        self.assertTrue(req.full_url.endswith('/v1/chat/completions'))
        self.assertEqual(json.loads(req.data)['messages'][0]['role'],'system')
        self.assertIn('[R1]',answer)


if __name__ == '__main__':
    unittest.main()
