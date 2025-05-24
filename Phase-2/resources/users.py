from flask_restful import Resource, reqparse, fields, marshal_with
from models import User
from db import SessionLocal
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

VALID_ROLES = ["Patient", "Doctor", "Admin"]

user_fields = {
    'id': fields.String,
    'username': fields.String,
    'email': fields.String,
    'role': fields.String,
    'is_active': fields.Boolean
}

parser = reqparse.RequestParser()
parser.add_argument("username", required=True)
parser.add_argument("password", required=True)
parser.add_argument("email", required=True)
parser.add_argument("role", required=True, choices=VALID_ROLES)  # Validates role

class UserListAPI(Resource):
    @marshal_with(user_fields)
    def get(self):
        session = SessionLocal()
        users = session.query(User).all()
        session.close()
        return users

    @marshal_with(user_fields)
    def post(self):
        args = parser.parse_args()
        session = SessionLocal()
        
        # Check for existing username/email
        existing_user = session.query(User).filter(
            (User.username == args["username"]) | (User.email == args["email"])
        ).first()
        if existing_user:
            session.close()
            return {"message": "Username or email already exists"}, 400

        try:
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

class UserAPI(Resource):
    @marshal_with(user_fields)
    def get(self, user_id):
        session = SessionLocal()
        user = session.query(User).get(user_id)
        session.close()
        if not user:
            return {"message": "User not found"}, 404
        return user

    @marshal_with(user_fields)
    def put(self, user_id):
        args = parser.parse_args()
        session = SessionLocal()
        user = session.query(User).get(user_id)
        if not user:
            session.close()
            return {"message": "User not found"}, 404

        try:
            # Check if new username/email conflicts with other users
            existing_user = session.query(User).filter(
                User.id != user_id,
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

    def delete(self, user_id):
        session = SessionLocal()
        user = session.query(User).get(user_id)
        if not user:
            session.close()
            return {"message": "User not found"}, 404
        session.delete(user)
        session.commit()
        session.close()
        return {"message": f"User {user_id} deleted"}, 200

from models import Admin

class AdminRegisterAPI(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", required=True)
        parser.add_argument("password", required=True)
        parser.add_argument("email", required=True)
        args = parser.parse_args()

        session = SessionLocal()
        try:
            # Check for existing username/email
            existing_user = session.query(User).filter(
                (User.username == args["username"]) | (User.email == args["email"])
            ).first()
            if existing_user:
                session.close()
                return {"message": "Username or email already exists"}, 400

            # Create user
            last_user = session.query(User).order_by(User.id.desc()).first()
            new_user_id = f"U{(int(last_user.id[1:]) + 1) if last_user else 1:03}"
            user = User(
                id=new_user_id,
                username=args["username"],
                password=generate_password_hash(args["password"]),
                email=args["email"],
                role="Admin"
            )
            session.add(user)

            # Create admin
            last_admin = session.query(Admin).order_by(Admin.id.desc()).first()
            new_admin_id = f"A{(int(last_admin.id[1:]) + 1) if last_admin else 1:03}"
            admin = Admin(
                id=new_admin_id,
                user_id=new_user_id
            )
            session.add(admin)

            session.commit()
            return {"message": f"Admin {admin.id} created and linked to user {user.id}"}, 201
        except IntegrityError:
            session.rollback()
            return {"message": "Database error occurred"}, 500
        finally:
            session.close()

class UserLoginAPI(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", required=True)
        parser.add_argument("password", required=True)
        args = parser.parse_args()

        session = SessionLocal()
        try:
            user = session.query(User).filter(User.username == args["username"]).first()
            if not user:
                return {"message": "Invalid username or password"}, 401

            if not check_password_hash(user.password, args["password"]):
                return {"message": "Invalid username or password"}, 401

            # Here you would typically create a session token
            # For now, we'll just return success and user info
            return {
                "message": "Login successful",
                "user_id": user.id,
                "role": user.role,
                "username": user.username
            }, 200
        finally:
            session.close()

class UserLogoutAPI(Resource):
    def post(self):
        # In a real implementation, you would invalidate the session token
        return {"message": "Logout successful"}, 200

class UserResetPasswordAPI(Resource):
    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("old_password", required=True)
        parser.add_argument("new_password", required=True)
        args = parser.parse_args()

        session = SessionLocal()
        try:
            user = session.query(User).get(user_id)
            if not user:
                return {"message": "User not found"}, 404

            if not check_password_hash(user.password, args["old_password"]):
                return {"message": "Invalid old password"}, 401

            user.password = generate_password_hash(args["new_password"])
            session.commit()
            return {"message": "Password reset successful"}, 200
        except IntegrityError:
            session.rollback()
            return {"message": "Database error occurred"}, 500
        finally:
            session.close()
