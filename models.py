from app import db
from sqlalchemy.dialects.postgresql import JSON



class Triples(db.Model):
    __tablename__ = 'Triples'

    id = db.Column(db.Integer, primary_key=True)
    gname = db.Column(db.String())
    subj = db.Column(db.String())
    pred = db.Column(db.String)
    obj = db.Column(db.String)
    notes = db.Column(JSON)

    def __init__(self, gname, subj, pred, obj):
        self.gname = gname
        self.subj = subj
        self.pred = pred
        self.obj = obj

    def __repr__(self):
        return '<id {}>'.format(self.id)



class GraphNames(db.Model):
    __tablename__ = 'graphname'

    id = db.Column(db.Integer, primary_key=True)
    gname = db.Column(db.String())

    def __init__(self, id, gname):
        self.id = id
        self.gname = gname

    def __repr__(self):
        return '<id {}>'.format(self.id)
