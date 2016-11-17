from app import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.types import DateTime



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
        return '<id {}: {}'.format(self.id, self.gname)


class DataMiningCache(db.Model):
    __tablename__ = 'dataminingcache'

    id = db.Column(db.Integer, primary_key=True)
    requestFrom = db.Column(JSON) # including from id, login-info
    requestTime = db.Column(DateTime)
    saasname = db.Column(db.String())
    saaspar = db.Column(JSON)
    saasresult = db.Column(JSON)

    def __init__(self, id, requestFrom, requestTime, saasName, saasPar, saasResult):
        self.id = id
        self.requestFrom = requestFrom
        self.requestTime = requestTime
        self.saasname = saasName
        self.saaspar = saasPar
        self.saasresult = saasResult

    def __rep__(self):
        return '<id {} :{} :{} :{} :{}>'.format(self.id, self.requestFrom, self.saasname, self.saaspar, self.saasresult)