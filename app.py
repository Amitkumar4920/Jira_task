from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_swagger_ui import get_swaggerui_blueprint
import datetime

app = Flask(__name__)

# Configuration for JWT
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change to a secure key
jwt = JWTManager(app)

# Initialize Flask-RESTful API
api = Api(app)

# Users will be stored in this dictionary for simplicity (in-memory)
users_db = {}

# Set up Swagger UI blueprint
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'  # We'll use a local JSON file for Swagger definition
swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Flask User API"})
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


# Resource for user signup
class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Simple validation
        if not username or not password:
            return {'message': 'Username and password are required'}, 400
        
        # Check if user already exists
        if username in users_db:
            return {'message': 'User already exists'}, 400
        
        # Hash password and save user to DB
        hashed_password = generate_password_hash(password)
        users_db[username] = {'password': hashed_password}
        
        return {'message': 'User created successfully'}, 201


# Resource for user login
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Validate input
        if not username or not password:
            return {'message': 'Username and password are required'}, 400

        user = users_db.get(username)
        if not user or not check_password_hash(user['password'], password):
            return {'message': 'Invalid username or password'}, 401

        # Create JWT token
        access_token = create_access_token(identity=username, fresh=True)
        return jsonify(access_token=access_token)


# Protected resource that requires JWT authentication
class Protected(Resource):
    @jwt_required()
    def get(self):
        return {'message': 'This is a protected route'}


# Add resources to the API
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Protected, '/protected')

# Main entry point for the Flask app
if __name__ == '__main__':
    app.run(debug=True)
