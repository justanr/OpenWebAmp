from collections import namedtuple

from app import app, db, ma, Album, Artist, Track, AlbumSerializer, ArtistSerializer, TrackSerializer, utils
from flask.ext.script import Manager

manager = Manager(app)

helper = namedtuple('helper', ['album', 'artist', 'track'])

models = helper(Album, Artist, Track)
serials = helper(AlbumSerializer, ArtistSerializer, TrackSerializer)


@manager.option('-d', '--dir', dest='dir')
def add(dir):
    
    out = "{0.name} - {1.name} - {2.position:0>2} - {2.name}"
    
    files = utils.walk(dir)
    tracks = (utils.TinyTag(f) for f in files)

    for t in tracks:
        artist, album, track = utils.store_metadata(t)
        print("Added: ", out.format(artist, album, track))


@manager.shell
def _shell_context():
    return dict(app=app, db=db, ma=ma, models=models, serials=serials, utils=utils)

if __name__ == "__main__":
    manager.run()
