from flask import request

from flask.ext.restful import Api, Resource

from . import models
from . import schemas

api = Api()

class SingleArtist(Resource):
    def get(self, id):
        artist = models.Artist.query.get_or_404(id)
        return {'artist':schemas.ArtistSchema(artist).data}

class SingleAlbum(Resource):
    def get(self, id):
        album = models.Album.query.get_or_404(id)
        return {'album':schemas.AlbumSchema(album).data}

class SingleTrack(Resource):
    def get(self, id):
        track = models.Track.query.get_or_404(id)
        return {'track':schemas.TrackSchema(track).data}

class ListArtist(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        q = models.Artist.query.order_by(models.Artist.name)
        page = q.paginate(page, limit, False)
        
        return {'artists':schemas.ArtistSchema(page.items, many=True).data}

class ListAlbum(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        q = models.Album.query.join(models.Artist)
        q = q.filter(models.Artist.id==models.Album.artist_id)
        q = q.order_by(models.Artist.name, models.Album.name)
        page = q.paginate(page, limit, False)
        
        return {'albums':schemas.AlbumSchema(page.items, many=True).data}

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

api.add_resource(SingleArtist, '/artist/<id>/', endpoint='artist')
api.add_resource(ListArtist, '/artist/', endpoint='artists')

api.add_resource(SingleAlbum, '/album/<id>/', endpoint='album')
api.add_resource(ListAlbum, '/album/', endpoint='albums')

api.add_resource(SingleTrack, '/track/<id>/', endpoint='track')
api.add_resource(ListTrack, '/track/', endpoint='tracks')
