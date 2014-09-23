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

    id = db.Column( db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128), nullable=False)
    playlists = db.relationship(
        'Playlist', 
        backref='owner', 
        order_by='Playlist.name'
        )
    name = db.Column(
        db.Unicode, 
        index=True, 
        unique=True, 
        nullable=False
        )
    bio = db.Column(
        db.UnicodeText, 
        default='Nickelback is my favorite band.'
        )
    email = db.Column(
        db.Unicode(256), 
        unique=True, 
        index=True, 
        nullable=False
        )
    permissions = db.Column(
        db.Integer,
        default=(
            Permissions.STREAM |
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
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.Unicode, 
        unique=True,
        index=True,
        nullable=False
        )
    albums = db.relationship('Album', backref='owner', order_by='Album.name')

    @classmethod
    def unique_hash(cls, name, **kwargs):
        return name

    @classmethod
    def unique_func(cls, query, name, **kwargs):
        return query.filter(cls.name == name)

class Track(db.Model, ReprMixin, UniqueMixin):
    __tablename__ = 'tracks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText, index=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    length = db.Column(db.Integer)
    location = db.Column(db.Unicode, unique=True)
    _trackpositions = db.relationship('TrackPosition', backref='track')
    # association_proxy allows easy access to an attribute on a
    # foreign relationship. In this case, the tracklist attribute
    # is being passed from the intermediate TrackPosition model
    tracklists = association_proxy('_trackpositions', 'tracklist')
    artist = db.relationship(
        'Artist', 
        backref=db.backref(
            'tracks',
            lazy='dynamic'
            )
        )
    stream = db.Column(
        db.String, 
        unique=True,
        default=lambda: str(uuid4())
        )

    @classmethod
    def unique_hash(cls, name, artist, location,  **kwargs):
        return name, artist, location

    @classmethod
    def unique_func(cls, query, name, artist, location,  **kwargs):
        return query.filter(
            cls.name == name, 
            cls.artist_id == artist.id,
            cls.location == location
            )

class TrackPosition(db.Model, ReprMixin):
    '''A many-to-many between the Track model and the Tracklist parent model.
    
    Information in this model is generated automatically by appending a track
    to a Tracklist's `tracks` attribute.
    '''

    __tablename__ = 'trackpositions'
    __repr_fields__ = ['tracklist', 'position', 'track']

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), index=True)
    tracklist_id = db.Column(
        db.Integer,
        db.ForeignKey('tracklists.id'),
        index=True
        )

    
class Tracklist(db.Model, ReprMixin, UniqueMixin):
    __tablename__ = 'tracklists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(128), index=True, nullable=False)
    type = db.Column(db.String(32))
    _trackpositions = db.relationship(
        'TrackPosition',
        backref='tracklist',
        # ordering_list will automatically update the position attribute
        # on the proxied Tracks. However, it must also be fed a correct
        # inital ordering.
        order_by='TrackPosition.position',
        collection_class=ordering_list('position')
        )
    tracks = association_proxy(
        '_trackpositions',
        'track',
        # A creator is needed to ensure we can simply append track
        # objects to a Tracklist's `track` attribute. The position
        # attribute is automatically filled in by ordering_list
        creator=lambda t: TrackPosition(track=t)
        )

    @property
    def length(self):
        '''Sums the length of all track objects associated with this tracklist.
        '''
        # TODO: Convert this to a `hybrid_property` so it is queryable
        return sum(t.length for t in self.tracks)

    @property
    def total_tracks(self):
        '''Provides the total number of tracks in a tracklist.'''
        #TODO: Convert this it `hybrid_property` so it is queryable
        return len(self.tracks)

    @classmethod
    def unique_hash(cls, name, owner, **kwargs):
        return name, owner

    @classmethod
    def unique_func(cls, query, name, owner, **kwargs):
        return query.filter(cls.name == name, cls.owner_id == owner.id)

    __mapper_args__ = {
        'polymorphic_on' : type,
        'with_polymorphic' : '*'
        }

class Album(Tracklist):
    __tablename__ = 'albums'

    id = db.Column(db.Integer, db.ForeignKey('tracklists.id'), primary_key=True)
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey('artists.id'),
        primary_key=True
        )

    __mapper_args__ = {
        'polymorphic_identity' : 'album',
        'inherit_condition' : (id == Tracklist.id)
        }

class Playlist(Tracklist):
    __tablename__ = 'playlists'

    id = db.Column(db.Integer, db.ForeignKey('tracklists.id'), primary_key=True)
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey('members.id'),
        primary_key=True
        )

    __mapper_args__ = {
        'polymorphic_identity' : 'playlist',
        'inherit_condition' : (id == Tracklist.id)
        }


