from app import db

class SportEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    sport = db.Column(db.String(100))
    participants = db.Column(db.Integer)
    area = db.Column(db.String(100))