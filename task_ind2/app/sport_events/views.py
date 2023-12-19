from sqlalchemy.exc import IntegrityError
from flask import jsonify, request, current_app
from . import sport_events_blueprint
from app import db, bcrypt, jwt
from .models import SportEvent
from app.auth.models import User
from flask_httpauth import HTTPBasicAuth
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, unset_jwt_cookies
import datetime
basicAuth = HTTPBasicAuth()

@basicAuth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return True
    return False

@basicAuth.error_handler
def unauthorized():
    return jsonify({"message":"Username or password incorrect!"}), 401

@sport_events_blueprint.route('/login', methods=['POST'])
@basicAuth.login_required
def login():
    username = basicAuth.username()
    user = User.query.filter_by(username=username).first()

    if user:
        token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify({'token': token, 'refresh_token': refresh_token}), 200
    
    return jsonify({'message': 'Token is not created!'}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify(
        {"message": "The token has been revoked.",
         "error": "token_revoked"}), 401

@sport_events_blueprint.route('/refresh', methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user, fresh=False)
    return jsonify({'token': new_token})

@sport_events_blueprint.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "logout successful"})
    unset_jwt_cookies(response)
    return response

@sport_events_blueprint.route('/sport_events', methods=['GET'])
def get_all_sport_events():
    sport_events = SportEvent.query.all()
    return_values = [
        {"id": sport_event.id, 
         "name": sport_event.name, 
         "sport": sport_event.sport,
         "participants": sport_event.participants,
         "area": sport_event.area}
         for sport_event in sport_events]

    return jsonify({'sport_events': return_values})

@sport_events_blueprint.route('/sport_events', methods=['POST'])
@jwt_required()
def post_sport_event():
    data_list = request.get_json()

    if not data_list:
        return jsonify({"message": "No input data provided"}), 400
    
    sport_events = []

    for new_data in data_list:
        if not all(key in new_data for key in ["name", "sport", "participants", "area"]):
            return jsonify({"message": "Missing keys in one or more entries. If data are correct, try to use square brackets"}), 422 

        sport_event = SportEvent(
            name=new_data['name'], 
            sport=new_data['sport'],
            participants=new_data['participants'],
            area=new_data['area']
        )

        db.session.add(sport_event)
        sport_events.append(sport_event)

    db.session.commit()

    result = []
    for new_sport_event in sport_events:
        result.append({
            "id": new_sport_event.id, 
            "name": new_sport_event.name, 
            "sport": new_sport_event.sport,
            "participants": new_sport_event.participants,
            "area": new_sport_event.area
        })

    return jsonify(result), 201

@sport_events_blueprint.route('/sport_events/<int:id>', methods=['PUT'])
@jwt_required()
def update_sport_event(id):
    sport_event = SportEvent.query.filter_by(id=id).first()
    
    if not sport_event:
        return jsonify({"message": f"sport event with id = {id} not found"}), 404
    
    new_data = request.get_json()
    
    if not new_data:
        return jsonify({"message": "no input data provided"}), 400
    
    if new_data.get('name'):
        sport_event.name = new_data.get('name')
    
    if new_data.get('sport'):
        sport_event.sport = new_data.get('sport')

    if new_data.get('participants'):
        sport_event.participants = new_data.get('participants')

    if new_data.get('area'):
        sport_event.area = new_data.get('area')

    try:
        db.session.commit()
        return jsonify({"message": "sport event was updated"}), 204
    except IntegrityError:
        db.session.rollback()

@sport_events_blueprint.route('/sport_events/<int:id>', methods=['GET'])
def get_sport_event(id):
    sport_event = SportEvent.query.get_or_404(id)
    return jsonify(
        {"id": sport_event.id, 
         "name": sport_event.name, 
         "sport": sport_event.sport,
         "participants": sport_event.participants,
         "area": sport_event.area})

@sport_events_blueprint.route('/sport_events/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_sport_event(id):
      sport_event = SportEvent.query.get(id)

      if not sport_event:
        return jsonify({"message": f"sport event with id = {id} not found"}), 404
      
      db.session.delete(sport_event)
      db.session.commit()
      return jsonify({"message" : "Resource successfully deleted."}), 200