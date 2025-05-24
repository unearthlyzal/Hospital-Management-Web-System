from flask_restful import Resource, reqparse, fields, marshal_with
from models import Department
from db import SessionLocal

# How we expose departments in JSON
department_fields = {
    'id':          fields.String,
    'name':        fields.String,
    'description': fields.String,
}

# Parser for POST/PUT
parser = reqparse.RequestParser()
parser.add_argument("name",        required=True)
parser.add_argument("description", required=False)

class DepartmentListAPI(Resource):
    @marshal_with(department_fields)
    def get(self):
        session = SessionLocal()
        depts = session.query(Department).all()
        session.close()
        return depts

    @marshal_with(department_fields)
    def post(self):
        args = parser.parse_args()
        session = SessionLocal()
        # generate ID like DEPT001
        last = session.query(Department).order_by(Department.id.desc()).first()
        num = int(last.id[4:]) + 1 if last else 1
        new_id = f"DEPT{num:03}"

        dept = Department(id=new_id, **args)
        session.add(dept)
        session.commit()
        session.refresh(dept)
        session.close()
        return dept, 201

class DepartmentAPI(Resource):
    @marshal_with(department_fields)
    def get(self, department_id):
        session = SessionLocal()
        dept = session.query(Department).get(department_id)
        session.close()
        if not dept:
            return {"message": "Department not found"}, 404
        return dept

    @marshal_with(department_fields)
    def put(self, department_id):
        args = parser.parse_args()
        session = SessionLocal()
        dept = session.query(Department).get(department_id)
        if not dept:
            session.close()
            return {"message": "Department not found"}, 404

        dept.name        = args["name"]
        dept.description = args.get("description")
        session.commit()
        session.refresh(dept)
        session.close()
        return dept, 200

    def delete(self, department_id):
        session = SessionLocal()
        dept = session.query(Department).get(department_id)
        if not dept:
            session.close()
            return {"message": "Department not found"}, 404
        session.delete(dept)
        session.commit()
        session.close()
        return {"message": f"Department {department_id} deleted"}, 200
