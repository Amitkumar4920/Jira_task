from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_restful import Api, Resource
from flasgger import Swagger, swag_from

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flash messages
api = Api(app)

# Swagger configuration
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "User Authentication API",
        "description": "API for signing up and signing in users",
        "version": "1.0"
    },
    "basePath": "/",
    "schemes": ["http"],
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)

# In-memory users database (for simplicity)
users_db = {}

# Routes for web interface
@app.route('/')
def home():
    return redirect(url_for('signin'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if users_db.get(username) == password:
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users_db:
            flash("User already exists", "danger")
            return redirect(url_for('signup'))
        users_db[username] = password
        flash("User created successfully", "success")
        return redirect(url_for('signin'))
    return render_template('signup.html')

# API endpoints
class SignUp(Resource):
    @swag_from({
        'tags': ['User Authentication'],
        'description': 'Register a new user',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string'},
                        'password': {'type': 'string'},
                    },
                    'required': ['username', 'password']
                }
            }
        ],
        'responses': {
            201: {
                'description': 'User created successfully',
                'schema': {'type': 'object', 'properties': {'message': {'type': 'string'}}}
            },
            400: {'description': 'User already exists'}
        }
    })
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if username in users_db:
            return {"message": "User already exists"}, 400

        users_db[username] = password
        return {"message": "User created successfully"}, 201

class SignIn(Resource):
    @swag_from({
        'tags': ['User Authentication'],
        'description': 'Log in an existing user',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string'},
                        'password': {'type': 'string'},
                    },
                    'required': ['username', 'password']
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Login successful',
                'schema': {'type': 'object', 'properties': {'message': {'type': 'string'}}}
            },
            401: {'description': 'Invalid credentials'}
        }
    })
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if users_db.get(username) == password:
            return {"message": "Login successful"}, 200
        return {"message": "Invalid credentials"}, 401

# Register API endpoints
api.add_resource(SignUp, '/api/signup', endpoint="signup_api")
api.add_resource(SignIn, '/api/signin', endpoint="signin_api")

if __name__ == '__main__':
    app.run(debug=True)
