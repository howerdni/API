import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category,DB_PATH


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client

        setup_db(self.app, DB_PATH)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_get_paginated_questions(self):
        res = self.client().get('/api/questions')
        data = json.loads(res.data) 
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_sent_requesting_questions_beyond_valid_page(self):
        res = self.client().get('/api/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')    

    def test_create_question(self):
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1,
            'difficulty': 1
        }
        num_of_questions_before = len(Question.query.all())
        res = self.client().post('/api/questions', json=new_question)
        data = json.loads(res.data)
        num_of_questions_after = len(Question.query.all())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(num_of_questions_after, num_of_questions_before + 1)

    def test_delete_question(self):
        question = Question(question='new question', answer='new answer',
                            difficulty=1, category=1)
        question.insert()
        question_id = question.id
        res = self.client().delete(f'/api/questions/{question_id}')
        data = json.loads(res.data)
        question = Question.query.filter(
            Question.id == question.id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)        


    def test_422_if_question_creation_fails(self):
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
        }
        res = self.client().post('/api/questions', json=new_question)
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


    def test_search_questions(self):
        search = {'searchTerm': 'movie'}
        res = self.client().post('/api/questions/search', json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions_list']),1)
        self.assertIsNotNone(data['total_questions_satisfy_condition'])


    def test_search_question_without_result(self):
        search = {'searchTerm': 'Facebook'}
        res = self.client().post('/api/questions/search', json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data['questions_list']),0)
        self.assertEqual(data['total_questions_satisfy_condition'],0)



    def test_retrieve_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_retrieve_questions_by_category_for_failed_get(self):
        res = self.client().get('/api/categories/a/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    def test_play_quiz(self):
        quiz_selection = {'previous_questions': [],
                          'quiz_category': {'type': 'Entertainment', 'id': 5}}
        res = self.client().post('/api/quizzes', json=quiz_selection)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_play_quiz_if_selection_missing(self):
        quiz_selection = {'previous_questions': []}
        res = self.client().post('/api/quizzes', json=quiz_selection)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")







# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()