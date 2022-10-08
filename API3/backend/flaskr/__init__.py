import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/api/categories')
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        categories_list = [category.format() for category in categories]

        return jsonify({
            'success': True,
            'categories': categories_list,
            'caregory_num':len(categories_list)
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/api/questions')
    def retrieve_all_questions():
        selection = Question.query.order_by(Question.id).all()
        questions_of_some_page = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.id).all()
        categories_list = [category.format() for category in categories]

        if len(questions_of_some_page) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': questions_of_some_page,
            'total_questions': len(selection),
            'categories': categories_list,
            'current_category': None
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/api/questions/<q_id>", methods=['DELETE'])
    def delete_question(q_id):
        try:
            question = Question.query.get(q_id)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': q_id
            })
        except:
            abort(422)


    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/api/questions", methods=['POST'])
    def create_question():
        body = request.get_json()
        if not (body.get('question',None) and body.get('answer',None) and body.get('category',None) and body.get('difficulty',None)):
            abort(422)
        try:
            question = Question(question=body.get('question',None),
            answer=body.get('answer',None),
            category=body.get('category',None),
            difficulty=body.get('difficulty',None)
            )
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            list_of_questions = [q.format() for q in selection]
            last_page_of_questions=list_of_questions[-QUESTIONS_PER_PAGE:]

            return jsonify({
                'success': True,
                'questions_list': last_page_of_questions,
            })

        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/api/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        if "searchTerm" in body:
            search_term = body['searchTerm'].strip()

        if search_term:
            search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

            return jsonify({
                'success': True,
                'questions_list': [q.format() for q in search_results],
                'total_questions_satisfy_condition': len(search_results),
            })
        else:
            abort(404)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:cat_id>/questions')
    def get_questions_by_category(cat_id):

        try:
            questions = Question.query.filter_by(category=str(cat_id)).all()
            return jsonify({
                'success': True,
                'questions': [q.format() for q in questions],
                'total_questions': len(questions),
                'categories': Category.query.get(cat_id).format(),
                'current_category': cat_id
            })
        except:
            abort(404)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/api/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        qz_category = body.get('quiz_category')
        previous_questions = body.get('previous_questions')


        try:
            if not (qz_category):
                abort(422)

            elif qz_category['type'] == 'click':
                candidate_questions = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()
            else:
            
                candidate_questions = Question.query.filter_by(
                    category=qz_category['id']).filter(Question.id.notin_(previous_questions)).all()
            list_of_candidate_question = candidate_questions[random.randrange(
                0, len(candidate_questions))].format() if len(candidate_questions) > 0 else None
            
            return jsonify({
                'success': True,
                'question': list_of_candidate_question
            })    
        except:
            abort(422)




    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400
    return app

