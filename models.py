from app import db
from sqlalchemy.dialects.postgresql import JSON


class Triples(db.Model):
    __tablename__ = 'Triples'

    id = db.Column(db.Integer, primary_key=True)
    subj = db.Column(db.String())
    pred = db.Column(db.String)
    obj = db.Column(db.String)
    notes = db.Column(JSON)

    def __init__(self, subj, pred, obj):
        self.subj = subj
        self.pred = pred
        self.obj = obj

    def __repr__(self):
        return '<id {}>'.format(self.id)
