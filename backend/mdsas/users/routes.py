from flask import request, Blueprint
from .models import database, User

user_routes = Blueprint('user_routes', __name__)


@user_routes.route('/createSU', methods=['POST'])
def create_secondary_user():
    payload = request.get_json()
    username = payload['secondaryUserName']
    email = payload['secondaryUserEmail']
    password = payload['secondaryUserPassword']
    admin = False

    if username and email and password:
        existing_user = User.query.filter(User.email == email).first()
        if existing_user:
            return {
                "status": 0,
                "message": "User already exists"
            }

        user = User(
            username=username,
            email=email,
            password=password,
            admin=admin
        )

        database.session.add(user)
        database.session.commit()

        return {
            "status": 1,
            "message": "Secondary User has been added."
        }

    return {
        "status": 0,
        "message": "Secondary User could not be added."
    }


@user_routes.route('/getSU', methods=['POST'])
def get_secondary_user():
    payload = request.get_json()
    email = payload['secondaryUserEmail']

    if email:
        existing_user: User = User.query.filter(User.email == email).first()
        if not existing_user:
            return {
                "status": 0,
                "message": "User does not exist"
            }

        return {
            "status": 1,
            "message": existing_user.__repr__()
        }

    return {
        "status": 0,
        "message": "Please provide valid email address"
    }


@user_routes.route('/suLogin', methods=['POST'])
def secondary_user_login():
    payload = request.get_json()
    email = payload['username']
    password = payload['password']

    if not email or not password:
        return {
            "status": 0,
            "message": "Username or password not provided"
        }

    existing_user: User = User.query.filter(
        (User.email == email) & (User.password == password) & (not User.admin)
    ).first()

    if not existing_user:
        return {
            "status": 0,
            "message": "User does not exist"
        }

    return {
        'status': 1,
        'id': existing_user.email,
        'userType': 'SU',
        'name': existing_user.username
    }


@user_routes.route('/adminLogin', methods=['POST'])
def admin_user_login():
    payload = request.get_json()
    email = payload['username']
    password = payload['password']

    if not email or not password:
        return {
            "status": 0,
            "message": "Username or password not provided"
        }

    existing_user: User = User.query.filter(
        (User.email == email) & (User.password == password) & (User.admin)
    ).first()

    if not existing_user:
        return {
            "status": 0,
            "message": "User does not exist"
        }

    return {
        'status': 1,
        'id': existing_user.email,
        'userType': 'ADMIN',
        'name': existing_user.username
    }


@user_routes.route('/checkEmailAvail', methods=['POST'])
def check_email_availability():
    payload = request.get_json()
    email = payload['email']

    if not email:
        return {
            "status": 0,
            "message": "Email not provided"
        }

    existing_user: User = User.query.filter(User.email == email).first()

    if not existing_user:
        return {
            "status": 1,
            "exists": 0,
            "message": "Email Address not in use."
        }

    return {
        "status": 0,
        "exists": 1,
        "message": "Email Address already in use."
    }
