from flask.ext.marshmallow import Marshmallow

from .utils.schema import Polymorphic, Length

# lowest common fields for serialized models
common = ('id', 'name')

ma = Marshmallow()

class BaseSchema(ma.Serializer):
    class Meta:
        additional = common

class TracklistSchema(BaseSchema): 
    tracks = ma.Nested('TrackSchema', only=common, many=True)
    owner = Polymorphic(
        mapping={
            'Member' : 'MemberSchema',
            'Artist' : 'ArtistSchema'
            },
        default_schema='BaseSchema',
        only=common
        )

class ArtistSchema(BaseSchema):
    albums = ma.Nested('TracklistSchema', only=common, many=True)

class MemberSchema(BaseSchema):
    bio = ma.String()
    playlists = ma.Nested('TracklistSchema', only=common, many=True)

class TrackSchema(BaseSchema):
    length = Length()
    stream = ma.String()
    artist = ma.Nested('ArtistSchema', only=common)
    tracklists = ma.Nested('TracklistSchema', only=common, many=True)
