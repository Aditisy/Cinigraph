import unittest
from unittest.mock import patch
import web_app

class WebTests(unittest.TestCase):
    def setUp(self):
        self.client=web_app.app.test_client()

    def test_rejects_cross_origin_generation(self):
        with patch('web_app.answer_question') as answer:
            r=self.client.post('/api/ask',json={'question':'Who directed The Matrix?'},
                               headers={'Origin':'https://unrelated.example'})
            self.assertEqual(r.status_code,403)
            answer.assert_not_called()

    def test_question_type_validation(self):
        r=self.client.post('/api/ask',json={'question':['not','text']})
        self.assertEqual(r.status_code,400)
        self.assertEqual(self.client.post('/api/ask',json=['invalid']).status_code,400)

    def test_unsupported_question(self):
        r=self.client.post('/api/ask',json={'question':'Who won an Oscar?'})
        self.assertEqual(r.status_code,400)
        self.assertIn('Unsupported',r.json['error'])

    def test_report_is_served(self):
        with self.client.get('/report.pdf') as r:
            self.assertEqual(r.status_code,200)
            self.assertEqual(r.mimetype,'application/pdf')

if __name__=='__main__':
    unittest.main()
