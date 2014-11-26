from flask import abort, request
from flask.ext.restful import Api
from . import models
from . import schemas
from .utils.api import SingleResource, ListResource

class SingleArtist(SingleResource):
    model = models.Artist
    schema = schemas.ArtistSchema

class SingleTrack(SingleResource):
    model = models.Track
    schema = schemas.TrackSchema

class SingleMember(SingleResource):
    model = models.Member
    schema = schemas.MemberSchema

class SingleTracklist(SingleResource):
    model = models.Tracklist
    schema = schemas.TracklistSchema

class SingleTag(SingleResource):
    model = models.Tag
    schema = schemas.TagSchema

class ListArtist(ListResource):
    model = models.Artist
    schema = schemas.ArtistSchema
    schema_opts = {'exclude' : ('albums', 'tags')}

class ListMember(ListResource):
    model = models.Member
    schema = schemas.MemberSchema
    schema_opts = {'exclude' : ('playlists', 'tags')}

class ListTracklist(ListResource):
    model = models.Tracklist
    schema = schemas.TracklistSchema
    schema_opts = {'exclude' : ('tracks',)}

class ListTrack(ListResource):
    model = models.Track
    schema = schemas.TrackSchema
    schema_opts = {'only' : ('id', 'name', 'links', 'artist')}

class ListTag(ListResource):
    model = models.Tag
    schema = schemas.TagSchema
    schema_opts = {'only' : ('id', 'name', 'links')}

api = Api()

api.add_resource(SingleTag, '/tag/<slug>/', endpoint='tag')
api.add_resource(ListTag, '/tag/', endpoint='tags')

api.add_resource(SingleArtist, '/artist/<slug>/', endpoint='artist')
api.add_resource(ListArtist, '/artist/', endpoint='artists')

api.add_resource(SingleTrack, '/track/<slug>/', endpoint='track')
api.add_resource(ListTrack, '/track/', endpoint='tracks')

api.add_resource(SingleMember, '/member/<slug>/', endpoint='member')
api.add_resource(ListMember, '/member/', endpoint='members')

api.add_resource(SingleTracklist, '/tracklist/<slug>/', endpoint='tracklist')
api.add_resource(ListTracklist, '/tracklist/', endpoint='tracklists')
