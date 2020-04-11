import os
import json
import random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)

  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  #@cross_origin()
  def categories():
    print('message: GET - /categories')

    categories_data = {}
    categorys = Category.query.order_by(Category.id).all()
    for category in categorys:
      categories_data[str(category.id)] = category.type
    
    result = {
      'categories': categories_data
    }
    return jsonify(result)

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
  def questions():
    print('message: GET - /questions')
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    all_questions = Question.query.order_by(Question.id).all()
    questions = [question.format() for question in all_questions]
    current_questions = questions[start:end]

    categories_data = categories().get_data().decode("utf-8")

    result = {
      'questions': current_questions,
      'total_questions': len(all_questions),
      'categories': json.loads(categories_data)['categories'],
      'current_category': ''  # what is value should be filled
    }
    #print(result)
    return jsonify(result)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_question(question_id):
    print('message: DELETE - /questions/question_id')
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success': True,
        'deleted': question_id
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
    print('message: POST - /questions')
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)

    try:
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      question.insert()

      return jsonify({
        'success': True
      })

    except:
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
  def search_questions():
    print('message: POST - /questions/search')
    
    total_questions = len(Question.query.all())

    tag = request.get_json().get('searchTerm', '')
    search = "%{}%".format(tag)
    all_questions = Question.query.filter(Question.question.ilike(search)).order_by(Question.id).all()
    questions = [question.format() for question in all_questions]

    result = {
      'questions': questions,
      'total_questions': total_questions,
      'current_category': ''  # what is value should be filled
    }
    print(result)
    return jsonify(result)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def category_questions(category_id):
    print('message: GET - /categories/category_id/questions')
    
    total_questions = len(Question.query.all())

    all_questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
    questions = [question.format() for question in all_questions]

    result = {
      'questions': questions,
      'total_questions': total_questions,
      'current_category': category_id
    }
    #print(result)
    return jsonify(result)

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
  def play():
    print('message: POST - /quizzes')
    
    body = request.get_json()

    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)

    all_questions = Question.query.filter(Question.category == int(quiz_category['id'])).order_by(Question.id).all()
    question = all_questions[random.randint(0, len(all_questions)-1)]

    result = {
      'previous_questions': previous_questions,
      'question': question.format()
    }
    #print(result)
    return jsonify(result)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "Unprocessable Entity"
    }), 422

  return app

    