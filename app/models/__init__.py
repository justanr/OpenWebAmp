from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declaratie_base, declared_attr
from sqlalchemy.orm import deferred
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy import Column, Sequence, Integer, String

Base = declarative_base()

class BaseMixin(object):
    __base_pattern__ = '<{class} {pattern}>'
    __repr_pattern__ = 'id:{id} name:{name}'
    __repr_fields__ = ['id', 'name']

    @declared_attr
    def __tablename__(self):
        '''Super lazy way of declaring table names.'''
        return self.__class__.__name__.lower() + 's'

    def __get_repr_fields(self):
        return {field:getattr(self, field, None) for field in self.__repr_fields__}

    def __repr__(self):
        pattern = self.__base_pattern__.format({'class':self.__class__.__name__,
                                                'pattern':self.__repr_pattern__}
                                                )
        fields = self.__get_repr_fields()
        return pattern.format(fields)

class PrimaryModel(BaseMixin):
    
    @declared_attr
    def id(self):
        name = '{}_id_seq'.format(self.__tablename__)
        return Column('id', Integer, Sequence(name), primary_key=True)

    @declared_attr
    def name(self):
        return Column('name', String(32), unique=True)

class Artist(PrimaryModel, Base):
    bio = Column('bio', Text, nullable=True)

class Member(PrimaryModel, Base):
    password = deferred(Column('password', String(256)), group='private')
    email = deferred(Column('email', String(256)), group='private')
    bio = deferred(Column('bio', String(64), nullable=True)

    reviews = relationship('Review', backref=backref('member', uselist=False))

class Review(PrimaryModel, Base):
    rating = Column('rating', Integer)
    review = Column('review', Text, nullable=True)

    member_id = Column('member_id', Integer, ForeignKey('members.id'))
    tracklist_id = Column('tracklist_id', Integer, ForeignKey('tracklists.id'))

class Track(PrimaryModel, Base):
    artist_id = Column('artist_id', Integer, ForiegnKey('artists.id'))
    artist = relationship('Artist', uselist=False)
    length = Column('length', Integer)
    stream = deferred(Column('stream', String(36), unique=True), group='streaming')
    location = deferred(Column('location', String(256), unique=True), group='streaming')

class Tracklist(PrimaryModel, Base):
    tracks = relationship('Track', secondary='tracks_to_tracklists', 
        backref=backref('tracklists', lazy='dynamic')
        )
    reiews = relationship('Reiew', backref=backref('tracklists', uselist=False))

    type = Column('type', String, default=__tablename__)
    __mapper_args__ = {
        'polymorphic_on':type,
        'with_polymorphic':'*'
        }

class Album(Tracklist):
    __tablename__ = 'albums'

    id = Column('id', Integer, Sequence('album_id_seq'), 
                ForeignKey('tracklists.id'), primary_key=True)
                )

    owner_id = Column('owner_id', Integer, ForeignKey('artists.id'))
    owner = relationship('Artist', backref='albums')

    __mapper_args__ = {
            'polymorphic_identity':__tablename__,
            'inherit_condition':(id == Tracklist.id)
            }

class Playlist(Tracklist):
    __tablename__ = 'playlists'

    owner_id = Column('owner_id', Integer, ForeignKey('members.id'))
    owner = relationship('Member', backref='playlists')

    __mapper_args__ = {
            'polymorphic_identity':__tablename__,
            'inherit_condition':(id == Tracklist.id)

member_tagged_artist = Table('member_tagged_artist',
                Column('member_id', Integer, ForeignKey('members.id')),
                Column('artist_id', Integer, ForeignKey('artists.id')),
                Column('tag_id', Integer, ForeignKey('tags.id')),
                UniqueConstraint('member_id', 'artist_id', 'tag_id', name='mta_uniq')
                )

tracks_to_tracklists = Table('tracks_to_tracklists',
                Column('track_id', Integer, ForeignKey('tracks.id'),
                Column('tracklist_id', Integer, ForeignKey('tracklists.id'),
                Column('position', Integer),
                CheckConstraint('position > 0', name='ttt_position_check_1'),
                UniqueConstraint('position', 'track_id', 'tracklist_id',
                        name='ttt_position_check_2')
                )
