from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Artist(db.Model):
    __tablename__ = 'artists'
    
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String, unique=True)
    albums = db.relationship('Album', backref=db.backref('artist', uselist=False))
    tracks = db.relationship('Track', backref=db.backref('artist', uselist=False))

class Album(db.Model):
    __tablename__ = 'albums'

    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String)
    artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'))
    tracks = db.relationship(
        'Track', backref=db.backref('album', uselist=False), lazy='immediate'
        )

class Track(db.Model):
    __tablename__ = 'tracks'

    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String)
    length = db.Column('length', db.Integer)
    position = db.Column('position', db.Integer)
    artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'))
    album_id = db.Column('album_id', db.Integer, db.ForeignKey('albums.id'))
