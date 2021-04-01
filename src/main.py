"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,Sale
from random import randint
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity)
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Endpoint para ver todos los usuarios
@app.route('/users', methods=['GET'])
def handle_users():
    users=User.query.all()
    response_body=[]
    for user in body:
        response_body.append(user.serialize())

    return jsonify(response_body), 200

#Endpoint para solicitar los datos de un usuario
@app.route('/users/<int:id>', methods=['GET'])
def handle_one_user(id):
    user=User.query.get(id)
    if user is None:
        return "NO EXISTE",404
    else:
        return jsonify(user.serialize()), 202

#Endpoint para crear un usuario
@app.route('/users', methods=['POST'])
def add_new_user():
    body= request.get_json()
    #validaciones de body para campos obligatorios 
    if isinstance (body,dict):
        if body is None:
            raise APIException("Please specify the request body as a json object", status_code=400)
        if 'email' not in body:
            raise APIException("You need to specify the name", status_code=400)
        if 'name' not in body:
            raise APIException("You need to specify the name", status_code=400)
        if 'password' not in body:
            raise APIException("You need to specify the name", status_code=400)
    else: return "error in body, is not a dictionary"
    user1 = User.create(
        email=body['email'],
        name=body['name'],
        password=body['password'])
    return user1.serialize(), 200

#endpoint para el login de un usuario 
@app.route("/login", methods=["POST"])
def handle_login():
    """ 
        check password for user with email = body['email']
        and return token if match.
        comprobar la contraseña del usuario con email = body ['email']
         y devolver el token si coincide.
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request / Falta JSON en la solicitud"}), 400
    params = request.get_json()
    email = params.get('email', None)
    password = params.get('password', None)
    if not email:
        return jsonify({"msg": "Missing email parameter / Falta el parametro de correo electronico"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter / Falta el parametro de contrasena"}), 400
    user = User.query.filter_by(email=email).one_or_none()
    if not user:
        return jsonify({"msg": "User does not exist / El usuario no existe"}), 404
    if user.check_password(password):
        jwt= create_access_token(identity=user.id)
        ret = user.serialize()
        ret["jwt"]=jwt
        return jsonify(ret), 200
    else:
        return jsonify({"msg": "Bad credentials / Credenciales incorrectas"}), 401

#endpoint para crear una venta
@app.route('/sales', methods=['POST'])
def add_new_sale():
    body= request.get_json()
    #validaciones de body para campos obligatorios
    if isinstance (body,dict):
        if body is None:
            raise APIException("Please specify the request body as a json object", status_code=400)
        if 'date' not in body:
            raise APIException("You need to specify date", status_code=400)
        if 'description' not in body:
            raise APIException("You need to specify description", status_code=400)
        if 'money_USD' not in body:
            raise APIException("You need to specify money", status_code=400)
        if 'user_id' not in body:
            raise APIException("You need to specify the id user", status_code=400)

    else: return "error in body, is not a dictionary"
    task1 = Task.create(
        date=body['date'],
        user_id=body['user_id'],
        description=body['description'],
        money_USD=body['money_USD'])
    return task1.serialize(), 200

@app.route('/sales/<int:id>',methods=["GET"])
def all_sales(id):
    user=User.query.get(id)
    if user is None:
        return "NO EXISTE",404
    if id is None:
        raise APIException('You need to specify an existing user', status_code=400)
    sales = Sale.query.filter_by(user_id=id)
    response_body= []
    for sale in sales:
        response_body.append(sale.serialize())
    return jsonify(response_body),200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=PORT, debug=False)
