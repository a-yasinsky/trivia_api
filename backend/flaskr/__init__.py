import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys
from  sqlalchemy.sql.expression import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [quest.format() for quest in selection]
  current_quests = questions[start:end]

  return current_quests

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
      return response

  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def retrieve_categries():

      selection = Category.query.order_by(Category.type).all()
      cats = {cat.id : cat.type for cat in selection}
      return jsonify({
          'success': True,
          'categories': cats,
          'total_categories': len(selection)
      })

  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
  @app.route('/questions', methods=['GET'])
  def retrieve_questions():
      selection = Category.query.order_by(Category.type).all()
      cats = {cat.id : cat.type for cat in selection}
      selection = Question.query.all()
      #GET categories and curr cat
      quests = paginate_questions(request, selection)
      return jsonify({
        'success': True,
        'questions': quests,
        'total_questions': len(selection),
        'categories': cats,
        'current_category': 'ALL'
      })
  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
      question = Question.query.get_or_404(question_id)
      try:
        question.delete()
        return jsonify({
            'success': True
        })
      except:
         abort(422)
  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
      body = request.get_json()

      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_difficulty = body.get('difficulty', None)
      new_category = body.get('category', None)

      try:
        question = Question(new_question,new_answer,new_category,new_difficulty)
        question.insert()

        return jsonify({
          'success': True
        })

      except:
        print(sys.exc_info())
        abort(422)
  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
  @app.route('/questions/search', methods=['POST'])
  def questions_search():
      search_term = request.get_json().get('searchTerm', '')
      selection = Question.query.filter(
        Question.question.ilike('%' + search_term + '%')
        ).all()
      questions = [quest.format() for quest in selection]
      return jsonify({
        'success': True,
        'questions': questions,
        'total_questions': len(questions),
        'current_category': 'ALL'
      })
  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
  @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
  def get_questions_by_category(cat_id):
      selection = Question.query.filter(Question.category == cat_id).all()
      questions = [quest.format() for quest in selection]
      return jsonify({
        'success': True,
        'questions': questions,
        'total_questions': len(questions),
        'current_category': cat_id
      })
  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_next_quize_question():
      body = request.get_json()

      previous_questions = body.get('previous_questions', [])
      quiz_category = body.get('quiz_category', {})
      question = Question.query. \
      filter(Question.category == quiz_category.get('id',0)). \
      filter(Question.id.notin_(previous_questions)). \
      order_by(func.random()).first()

      question = question.format() if question else None
      return jsonify({
        'success': True,
        'question': question
      })
  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "erorr": 404,
      "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
      "success": False,
      "erorr": 422,
      "message": "unprocessable entity"
    }), 422

    @app.errorhandler(400)
    def not_found(error):
      return jsonify({
        "success": False,
        "erorr": 400,
        "message": "bad request"
      }), 400

      @app.errorhandler(500)
      def not_found(error):
        return jsonify({
          "success": False,
          "erorr": 500,
          "message": "internal server error"
        }), 500

  return app
