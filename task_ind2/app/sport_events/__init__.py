from flask import Blueprint

sport_events_blueprint = Blueprint('sport_events_bp', __name__, template_folder="templates/sport_events")

from . import views