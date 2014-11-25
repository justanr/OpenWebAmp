from flask import abort, request

from flask.ext.restful import Api, Resource

from . import models
from . import schemas
from .utils.api import SingleResource

api = Api()

class SingleArtist(SingleResource):
    model = models.Artist
    schema = schemas.ArtistSchema
    json_root = 'artist'

class SingleTrack(SingleResource):
    model = models.Track
    schema = schemas.TrackSchema
    json_root = 'track'

class SingleMember(SingleResource):
    model = models.Member
    schema = schemas.MemberSchema
    json_root = 'member'

class SingleTracklist(SingleResource):
    model = models.Tracklist
    schema = schemas.TracklistSchema
    json_root = 'tracklist'

class SingleTag(SingleResource):
    model = models.Tag
    schema = schemas.TagSchema
    json_root = 'tag'
    

class ListArtist(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        q = models.Artist.query.order_by(models.Artist.name)
        page = q.paginate(page, limit, False)
        
        serializer = schemas.ArtistSchema(
            page.items,
            many=True,
            exclude=(
                'albums',
                'tags'
                )
            )

        return {'artists':serializer.data}

class ListMember(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        q = models.Member.query.order_by(models.Member.name)
        page = q.paginate(page, limit, False)

        serializer = schemas.MemberSchema(
            page.items, 
            many=True,
            exclude=('playlists', 'tags')
            )

        return {'members' : serializer.data}


class ListTracklist(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)
        tl_type = request.args.get('type', default=None)

        q = models.Tracklist.query.order_by(models.Tracklist.name)

        if tl_type and tl_type in ['album', 'playlist']:
            q = q.filter(models.Tracklist.type == tl_type)

        page = q.paginate(page, limit, False)

        serializer = schemas.TracklistSchema(
            page.items, 
            exclude=('tracks',),
            many=True
            )

        return {'tracklists' : serializer.data}


class ListTrack(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        q = models.Track.query.join(models.Artist)
        q = q.filter(
            models.Artist.id==models.Album.owner_id
            )
        q = q.order_by(
            models.Track.name,
            models.Artist.name
            )
        page = q.paginate(page, limit, False)
       
        serializer = schemas.TrackSchema(
            page.items, 
            many=True,
            only=('id', 'name', 'links', 'artist')
            )

        return {'tracks':serializer.data}

class ListTag(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        q = models.Tag.query.order_by(models.Tag.name)
        page = q.paginate(page, limit, False)

        serializer = schemas.TagSchema(
            page.items, 
            only=(
                'id', 
                'name', 
                'links'
                ), 
            many=True
            )

        return {'tags' : serializer.data}


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
