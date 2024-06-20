import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
def get_drinks():
    try:
        # fetch all drinks from the database
        drinks = Drink.query.all()

        # format the drinks using the short() method
        drinks_short = [drink.short for drink in drinks]

        #return response 
        return jsonify({
            'success': True,
            'drinks': drinks_short
        }), 200
    except Exception as e:
        # Handle any errors that occur
        print(f"Error: {e}")
        abort(500)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        # fetch the relevant drink from the database
        drinks = Drink.query.all()

        # format the drinks using the drink.long() method
        drink_long = [drink.long for drink in drinks]

        #return response 
        return jsonify({
            'success': True,
            'drinks': drink_long
        }), 200
    except Exception as e:
        # Handle any errors that occur
        print(f"Error: {e}")
        abort(500)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    # extract JSON body from the reques
    body = request.get_json()
    # validate the response data
    if not body:
        abort(400, description="Request does not contain a valid JSON body")
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if not title or not recipe:
        abort(400, description="Title and recipe are required")
    try:
        # create new drink object and save it in the database
        new_drink = Drink(title = title, recipe = json.dumps(recipe))
        new_drink.insert()
         
        #return response 
        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        }), 200
    except Exception as e:
        # Handle any errors that occur
        print(f"Error: {e}")
        abort(500)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):
    body = request.get_json()

    if not body:
        abort(400, description="Request does not contain a valid JSON body")
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_more()

        if drink is none:
            abort(404, description=f"Drink woth id {id} not found")

        if title:
            drink.title = title
        if recipe:
            drink.recipe = json.dumps(recipe)
        
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception as e:
        # Handle any errors that occur
        print(f"Error: {e}")
        abort(500)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_more()

        if drink is none:
            abort(404, description=f"Drink woth id {id} not found")

        
        drink.delete()

        return jsonify({
            'success': True,
            'drinks': id
        }), 200
    except Exception as e:
        # Handle any errors that occur
        print(f"Error: {e}")
        abort(500)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify({
        "success": False,
        "error": ex.status_code,
        "message": ex.error
    })
    response.status_code = ex.status_code
    return response 


if __name__ == "__main__":
    app.debug = True
    app.run()
