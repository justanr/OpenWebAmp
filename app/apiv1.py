from flask import request

from flask.ext.restful import Api, Resource

from . import models
from . import schemas

api = Api()

class SingleArtist(Resource):
    def get(self, id):
        artist = models.Artist.query.get_or_404(id)
        return {'artist':schemas.ArtistSchema(artist).data}


class SingleTrack(Resource):
    def get(self, id):
        track = models.Track.query.get_or_404(id)
        return {'track':schemas.TrackSchema(track).data}


class SingleMember(Resource):
    def get(self, id):
        member = models.Member.query.get_or_404(id)
        return {'member' : schemas.MemberSchema(member).data}


class SingleTracklist(Resource):
    def get(self, id):
        tracklist = models.Tracklist.query.get_or_404(id)
        return {'tracklist' : schemas.TracklistSchema(tracklist).data}


class SingleTag(Resource):
    def get(self, id):
        tag = models.Tag.query.get_or_404(id)
        return {'tag' : schemas.TagSchema(tag).data}


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

        q = models.Tracklist.query.order_by(models.Tracklist.name)
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

        q = models.Track.query.join(models.Artist,Album)
        q = q.filter(
            models.Artist.id==models.Album.artist_id,
            models.Album.id==models.Track.album_id
            )
        q = q.order_by(
            models.Artist.name, 
            models.Album.name, 
            models.Track.position
            )
        page = q.paginate(page, limit, False)
        
        return {'tracks':schemas.TrackSchema(page.items, many=True).data}


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


api.add_resource(SingleTag, '/tag/<id>/', endpoint='tag')
api.add_resource(ListTag, '/tag/', endpoint='tags')

api.add_resource(SingleArtist, '/artist/<id>/', endpoint='artist')
api.add_resource(ListArtist, '/artist/', endpoint='artists')

api.add_resource(SingleTrack, '/track/<id>/', endpoint='track')
api.add_resource(ListTrack, '/track/', endpoint='tracks')

api.add_resource(SingleMember, '/member/<id>/', endpoint='member')
api.add_resource(ListMember, '/member/', endpoint='members')

api.add_resource(SingleTracklist, '/tracklist/<id>/', endpoint='tracklist')
api.add_resource(ListTracklist, '/tracklist/', endpoint='tracklists')
