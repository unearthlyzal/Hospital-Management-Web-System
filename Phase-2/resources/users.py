from flask_restful import Resource, reqparse, fields, marshal_with
from models import User
from db import SessionLocal

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
parser.add_argument("role", required=True)  # "Patient", "Doctor", "Admin"

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
        last = session.query(User).order_by(User.id.desc()).first()
        if last:
            last_num = int(last.id[1:])
        else:
            last_num = 0
        new_id = f"U{last_num + 1:03}"

        new_user = User(id=new_id, **args)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        session.close()
        return new_user, 201

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

        user.username = args["username"]
        user.password = args["password"]
        user.email = args["email"]
        user.role = args["role"]

        session.commit()
        session.refresh(user)
        session.close()
        return user

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

        # Create user
        last_user = session.query(User).order_by(User.id.desc()).first()
        new_user_id = f"U{(int(last_user.id[1:]) + 1) if last_user else 1:03}"
        user = User(
            id=new_user_id,
            username=args["username"],
            password=args["password"],
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
        session.close()
        return {"message": f"Admin {admin.id} created and linked to user {user.id}"}, 201
