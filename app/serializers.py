from flask.ext.marshmallow import Marshmallow

from .utils.schema import Polymorphic, Length

# lowest common fields for serialized models
common = ('id', 'name')

class BaseSchema(ma.Serializer):
    class Meta:
        additional = common

class AlbumSchema(BaseSchema):
    artist = ma.Nested('ArtistSchema', only=common)

class ArtistSchema(BaseSchema):
    albums = ma.Nested('AlbumSchema', only=common, many=True)
    tracks = ma.Nested('TrackSchema', exclude=('album', 'artist'), many=True)

class MemberSchema(BaseSchema):
    bio = ma.String()

class TrackSchema(BaseSchema):
    length = Length()
    position = ma.Integer()
    stream = ma.String()
    artist = ma.Nested('ArtistSchema', only=common)
    album = ma.Nested('AlbumSchema', only=common)
