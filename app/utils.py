import os
from hashlib import sha256

from mutagenx import File
from .models import db, Album, Artist, Track

valid_types=('m4a', 'flac', 'mp3', 'ogg', 'oga')


def find(basedir, valid_types=valid_types):
    '''Utilize os.walk to only select out the files we'd like to potentially
    parse and yield them one at a time.'''
    basedir = os.path.abspath(basedir)
    for current, dirs, files in os.walk(basedir):
        if not files:
            continue
        for file in files:
            if file.endswith(valid_types):
                yield os.path.join(os.path.abspath(current), file)

def adaptor(track):
    stream = "{}{}{}{}".format(
        track['artist'][0], track['album'][0], 
        track['tracknumber'][0], track['tracknumber'][0]
        )
    stream = stream.encode('ascii', 'xmlcharrefreplace')
    stream = sha256(stream).hexdigest()

    return dict(
        artist=track['artist'][0],
        album=track['album'][0],
        position=int(track['tracknumber'][0].split('/')[0]),
        length=int(track.info.length),
        location=track.filename,
        name=track['title'][0],
        stream=stream
        )

def adapt_track(track, adaptor=adaptor):

    info = adaptor(track)

    artist = Artist.query.filter(Artist.name == info['artist']).first()
    if not artist:
        artist = Artist(name=info['artist'])
        db.session.add(artist)
    info['artist'] = artist

    album = Album.query.filter(Album.name==info['album']).first()
    if not album:
        album = Album(name=info['album'], artist=artist)
        db.session.add(album)
    info['album'] = album

    track = Track.query.filter(Track.name==info['name'])
    track = track.filter(Track.album_id==album.id)
    track = track.first()
    if not track:
        track = Track(**info)
        db.session.add(track)

    return artist, album, track


def store_directory(basedir, valid_types=valid_types, adaptor=adaptor):
    for file in find(basedir, valid_types):
        file = File(file, easy=True)
        artist, album, track = adapt_track(file)
        print(
            " * Storing: {0.name} - {1.name} - {2.position:2>0} - {2.name}"
            "".format(artist, album, track))
        db.session.commit()
