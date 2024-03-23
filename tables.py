from extension import db


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    year = db.Column(db.Integer)
    director = db.Column(db.Integer, db.ForeignKey('directors.id'))
    length = db.Column(db.String)
    rating = db.Column(db.Integer)


class Director(db.Model):
    __tablename__ = 'directors'
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(100))