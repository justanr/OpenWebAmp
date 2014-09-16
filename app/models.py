from uuid import uuid4
from datetime import datetime

from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

from werkzeug import generate_password_hash, check_password_hash

from .utils.models import ReprMixin, UniqueMixin
from .utils.perms import Permissions

db = SQLAlchemy()

class Member(db.Model, ReprMixin, UniqueMixin):
    __tablename__ = 'members'

    id = db.Column('id', db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(
        'name', db.Unicode, 
        index=True, 
        unique=True, 
        nullable=False
        )
    bio = db.Column(
        'bio', 
        db.UnicodeText, 
        default='Nickelback is my favorite band.'
        )
    email = db.Column(
        'email', 
        db.Unicode(256), 
        unique=True, 
        index=True, 
        nullable=False
        )
    permissions = db.Column(
        'permissions', db.Integer,
        default=(
            Permissions.STREAM |
            Permissions.REVIEW |
            Permissions.TAG
            ),
        index=True
        )

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    @property
    def password(self):
        raise AttributeError("password is a non-readable field")

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permission):
        return self.permissions is not None and \
            (self.permissions & permission) == permission

    @classmethod
    def unique_hash(cls, name, email, **kwargs):
        return name, email

    @classmethod
    def unique_func(cls, query, name, email, **kwargs):
        return query.filter(cls.name == name, cls.email == email)


class Artist(db.Model, ReprMixin, UniqueMixin):
    __tablename__ = 'artists'
    
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.Unicode, unique=True)
    albums = db.relationship(
        'Album', 
        backref=db.backref(
            'artist', 
            uselist=False
            ),
        order_by='Album.name'
        )
    tracks = db.relationship(
        'Track', 
        backref=db.backref(
            'artist', 
            uselist=False
            ),
        lazy='noload'
        )

    @classmethod
    def unique_hash(cls, name, **kwargs):
        return name

    @classmethod
    def unique_func(cls, query, name, **kwargs):
        return query.filter(cls.name == name)

class Album(db.Model):
    __tablename__ = 'albums'

    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.Unicode)
    artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'))
    tracks = db.relationship(
        'Track', 
        backref=db.backref(
            'album', 
            uselist=False
            ),
        order_by='Track.position'
        )

    @classmethod
    def unique_hash(cls, name, artist, **kwargs):
        return name, artist

    @classmethod
    def unique_func(cls, query, name, artist, **kwargs):
        return query.filter(cls.name == name, cls.artist_id == artist.id)

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

    @classmethod
    def unique_hash(cls, name, artist, location,  **kwargs):
        return name, artist, location

    @classmethod
    def unique_func(cls, session, name, artist, location,  **kwargs):
        return query.filter(
            cls.name == name, 
            cls.artist_id == artist.id,
            cls.location == location
            )
