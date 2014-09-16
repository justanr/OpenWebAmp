from flask import request, abort, send_file
from flask.ext.restful import Api, Resource

from .config import configs
from .models import db, Artist, Album, Track
from .serializers import ma, ArtistSchema, AlbumSchema, TrackSchema
from .utils.factory import create_app
from .utils import Permissions


# Setup
config = configs.get('dev')
app = create_app(__name__, config, exts=[db, ma])
api = Api(app)


# API Endpoints
class SingleArtist(Resource):
    def get(self, id):
        artist = Artist.query.get_or_404(id)
        return {'artist':ArtistSchema(artist).data}

class SingleAlbum(Resource):
    def get(self, id):
        album = Album.query.get_or_404(id)
        return {'album':AlbumSchema(album).data}

class SingleTrack(Resource):
    def get(self, id):
        track = Track.query.get_or_404(id)
        return {'track':TrackSchema(track).data}

class ListArtist(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        q = Artist.query.order_by(Artist.name)
        page = q.paginate(page, limit, False)
        
        return {'artists':ArtistSchema(page.items, many=True).data}

class ListAlbum(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        q = Album.query.join(Artist).filter(Artist.id==Album.artist_id)
        q = q.order_by(Artist.name, Album.name)
        page = q.paginate(page, limit, False)
        
        return {'albums':AlbumSchema(page.items, many=True).data}

class ListTrack(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        q = Track.query.join(Artist,Album)
        q = q.filter(Artist.id==Album.artist_id,Album.id==Track.album_id)
        q = q.order_by(Artist.name, Album.name, Track.position)
        page = q.paginate(page, limit, False)
        
        return {'tracks':TrackSchema(page.items, many=True).data}

@app.route('/stream/<stream_id>', methods=['GET'])
def stream(stream_id):
    track = Track.query.filter(Track.stream==stream_id).first()
    if not track:
        abort(404)

    filename = track.location
    return send_file(filename)

api.add_resource(SingleArtist, '/artist/<id>/', endpoint='artist')
api.add_resource(ListArtist, '/artist/', endpoint='artists')

api.add_resource(SingleAlbum, '/album/<id>/', endpoint='album')
api.add_resource(ListAlbum, '/album/', endpoint='albums')

api.add_resource(SingleTrack, '/track/<id>/', endpoint='track')
api.add_resource(ListTrack, '/track/', endpoint='tracks')
