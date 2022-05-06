"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    is_user = User.query.filter_by(email=email).first()

    if is_user.email != email or is_user.password != password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():
    user_query = User.query.all()
    all_user = list(map(lambda x: x.serialize(), user_query))
    return jsonify(all_user), 200

@app.route('/user', methods=['POST'])
def create_User():
    # You have to request a body before anything else
    body=request.get_json()
    # the request.get_json is everything in the body your trying to send in postman
    if 'email' not in body:
        raise APIException('bad request, email needed', status_code=400)
    if 'password' not in  body:
        raise APIException('bad request, password needed', status_code=400)
    if 'is_active' not in body:
                raise APIException('bad request, is_active needed', status_code=400)
    user1 = User(email=body['email'], password=body['password'], is_active=body['is_active'])
    db.session.add(user1)
    db.session.commit()
    return jsonify(user1.serialize())

@app.route('/user/<int:user_id>', methods=['GET'])
def userID(user_id):
    user = User.query.get(user_id)
    return jsonify(user.email), 200
# YOU HAVE TO HAVE SERIALIZE BECAUSE OF WHAT ITS RETURNING

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
