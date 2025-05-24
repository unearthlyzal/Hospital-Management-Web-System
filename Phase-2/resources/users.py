from flask_restful import Resource, reqparse, marshal_with
from flask import request, jsonify
from flask_restx import Namespace, Api, fields as restx_fields
from models import User, Doctor, Patient
from db import SessionLocal
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from auth import admin_required, get_current_user, generate_token
from validators import validate_user_data

VALID_ROLES = ["Patient", "Doctor", "Admin"]

# Define fields using flask_restx fields
user_fields = {
    'id': restx_fields.String,
    'username': restx_fields.String,
    'email': restx_fields.String,
    'role': restx_fields.String,
    'is_active': restx_fields.Boolean
}

parser = reqparse.RequestParser()
parser.add_argument("username", required=True)
parser.add_argument("password", required=True)
parser.add_argument("email", required=True)
parser.add_argument("role", required=True, choices=VALID_ROLES)  # Validates role

ns = Namespace('users', description='User operations')

# Create API instance for Swagger documentation
api = Api()

@ns.route('')
class UserList(Resource):
    @admin_required
    @marshal_with(user_fields)
    def get(self):
        session = SessionLocal()
        users = session.query(User).all()
        session.close()
        return users

    @admin_required
    @marshal_with(user_fields)
    def post(self):
        args = parser.parse_args()
        validate_user_data(args)
        
        session = SessionLocal()
        try:
            # Check for existing username/email
            existing_user = session.query(User).filter(
                (User.username == args["username"]) | (User.email == args["email"])
            ).first()
            if existing_user:
                session.close()
                return {"message": "Username or email already exists"}, 400

            last = session.query(User).order_by(User.id.desc()).first()
            if last:
                last_num = int(last.id[1:])
            else:
                last_num = 0
            new_id = f"U{last_num + 1:03}"

            new_user = User(
                id=new_id,
                username=args["username"],
                password=generate_password_hash(args["password"]),
                email=args["email"],
                role=args["role"]
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            session.close()
            return new_user, 201
        except IntegrityError:
            session.rollback()
            session.close()
            return {"message": "Database error occurred"}, 500

@ns.route('/<string:id>')
class UserResource(Resource):
    @admin_required
    @marshal_with(user_fields)
    def get(self, id):
        session = SessionLocal()
        user = session.query(User).get(id)
        session.close()
        if not user:
            return {"message": "User not found"}, 404
        return user

    @admin_required
    @marshal_with(user_fields)
    def put(self, id):
        args = parser.parse_args()
        validate_user_data(args)
        
        session = SessionLocal()
        user = session.query(User).get(id)
        if not user:
            session.close()
            return {"message": "User not found"}, 404

        try:
            # Check if new username/email conflicts with other users
            existing_user = session.query(User).filter(
                User.id != id,
                (User.username == args["username"]) | (User.email == args["email"])
            ).first()
            if existing_user:
                session.close()
                return {"message": "Username or email already exists"}, 400

            user.username = args["username"]
            user.password = generate_password_hash(args["password"])
            user.email = args["email"]
            user.role = args["role"]

            session.commit()
            session.refresh(user)
            session.close()
            return user
        except IntegrityError:
            session.rollback()
            session.close()
            return {"message": "Database error occurred"}, 500

    @admin_required
    def delete(self, id):
        session = SessionLocal()
        user = session.query(User).get(id)
        if not user:
            session.close()
            return {"message": "User not found"}, 404
        session.delete(user)
        session.commit()
        session.close()
        return {"message": f"User {id} deleted"}, 200

@ns.route('/me')
class CurrentUser(Resource):
    @marshal_with(user_fields)
    def get(self):
        user = get_current_user()
        if not user:
            return {"message": "Not authenticated"}, 401
        return user

    @marshal_with(user_fields)
    def put(self):
        args = parser.parse_args()
        validate_user_data(args)
        
        user = get_current_user()
        if not user:
            return {"message": "Not authenticated"}, 401

        session = SessionLocal()
        try:
            # Check if new username/email conflicts with other users
            existing_user = session.query(User).filter(
                User.id != user.id,
                (User.username == args["username"]) | (User.email == args["email"])
            ).first()
            if existing_user:
                session.close()
                return {"message": "Username or email already exists"}, 400

            user.username = args["username"]
            user.password = generate_password_hash(args["password"])
            user.email = args["email"]

            session.commit()
            session.refresh(user)
            session.close()
            return user
        except IntegrityError:
            session.rollback()
            session.close()
            return {"message": "Database error occurred"}, 500

class UserLoginAPI(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", required=True)
        parser.add_argument("password", required=True)
        args = parser.parse_args()

        session = SessionLocal()
        try:
            user = session.query(User).filter(User.username == args["username"]).first()
            if not user or not check_password_hash(user.password, args["password"]):
                return {"message": "Invalid credentials"}, 401

            token = generate_token(user.id, user.role)
            return {"token": token, "user": marshal_with(user_fields)(lambda: user)()}, 200
        finally:
            session.close()

class UserLogoutAPI(Resource):
    def post(self):
        # In a real implementation, you would invalidate the session token
        return {"message": "Successfully logged out"}, 200
