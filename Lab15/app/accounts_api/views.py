from flask import jsonify, make_response, request
from flask_restful import Api, Resource
from marshmallow import ValidationError
from app.auth.models import User
from . import accounts_api_blueprint
from .schemas import SingleUserSchema, MultipleUsersSchema, GetSingleUserSchema
from app import db, bcrypt

api = Api(accounts_api_blueprint)
single_user_schema = SingleUserSchema()

multiple_users_schema = MultipleUsersSchema(many=True)

class HelloWorld(Resource):
    def get(self):
        return {"hello": "world"}
    
class UsersApi(Resource):
    def get(self):
        users = User.query.all()
        return make_response(jsonify({'users': multiple_users_schema.dump(users)}), 200)

    def post(self):
        try:
            data = request.get_json()
            user = single_user_schema.load(data)
        except ValidationError as err:
            errors = {field: messages[0] if isinstance(messages, list) else messages for field, messages in err.messages.items()}
            return make_response(jsonify(errors), 400)

        new_user = User(**user)
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception:
            return make_response(jsonify({'message': 'User data has been duplicated'}), 400)

        return make_response(jsonify({'message': 'User has been created'}), 201)

class UserApi(Resource):
    get_single_user_schema = GetSingleUserSchema()
    single_user_schema = SingleUserSchema()
    multiple_users_schema = MultipleUsersSchema(many=True)

    def get(self, id):
        user = User.query.get(id)
        if not user:
            return make_response(jsonify({'message': 'User not found'}), 404)

        user_data = self.get_single_user_schema.dump(user)
        return make_response(jsonify(user_data), 200)

    def put(self, id):
        user = User.query.get(id)
        if not user:
            return make_response(jsonify({'message': 'User not found'}), 404)

        try:
            data = self.single_user_schema.load(request.get_json(), partial=True)  # Enable partial loading
            if 'password' in data:
                hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
                data['password'] = hashed_password

            for key, value in data.items():
                setattr(user, key, value)

            db.session.commit()
        except ValidationError as err:
            errors = {field: messages[0] if isinstance(messages, list) else messages for field, messages in
                      err.messages.items()}
            return make_response(jsonify(errors), 400)
        except Exception:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to update user'}), 400)

        return make_response(jsonify({'message': 'User has been updated'}), 200)

    def delete(self, id):
        user = User.query.get(id)
        if not user:
            return make_response(jsonify({'message': 'User not found'}), 404)

        try:
            db.session.delete(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return make_response(jsonify({'message': 'Failed to delete user'}), 400)

        return make_response(jsonify({'message': 'User has been deleted'}), 200)

api.add_resource(HelloWorld, '/hello')
api.add_resource(UsersApi, '/users')
api.add_resource(UserApi, '/user/<int:id>')