from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Artist(db.Model):
    __tablename__ = 'artists'
    
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.Unicode, unique=True)
    albums = db.relationship(
        'Album', 
        backref=db.backref('artist', uselist=False),
        order_by='Album.name'
        )
    tracks = db.relationship(
        'Track', 
        backref=db.backref('artist', uselist=False),
        lazy='noload'
        )

class Album(db.Model):
    __tablename__ = 'albums'

    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.Unicode)
    artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'))
    tracks = db.relationship(
        'Track', 
        backref=db.backref('album', uselist=False), 
        lazy='immediate',
        order_by='Track.position'
        )

class Track(db.Model):
    __tablename__ = 'tracks'

    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.Unicode)
    length = db.Column('length', db.Integer)
    position = db.Column('position', db.Integer)
    artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'))
    album_id = db.Column('album_id', db.Integer, db.ForeignKey('albums.id'))
    location = db.Column('location', db.Unicode, unique=True)
    stream = db.Column('stream', db.String, unique=True)
