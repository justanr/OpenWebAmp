import os
from uuid import uuid4
from time import time

from mutagenx import File

from .. import models

valid_types=('m4a', 'flac', 'mp3', 'ogg', 'oga')


def find(basedir, valid_types=valid_types):
    '''Utilize os.walk to only select out the files we'd like to potentially
    parse and yield them one at a time.'''
    basedir = os.path.abspath(basedir)
    for current, dirs, files in os.walk(basedir):
        if not files:
            continue
        for file in sorted(files):
            if file.endswith(valid_types):
                yield os.path.join(os.path.abspath(current), file)

def adaptor(track):
    return dict(
        artist=track['artist'][0],
        album=track['album'][0],
        length=int(track.info.length),
        location=track.filename,
        name=track['title'][0],
        )

def adapt_track(track, adaptor=adaptor):

    info = adaptor(track)

    artist = models.Artist.find_or_create(
        models.db.session,
        name=info['artist']
        )
    album = models.Album.find_or_create(
        models.db.session,
        name=info.pop('album'),
        owner=artist
        )
    info['artist'] = artist
    track = models.Track.find_or_create(models.db.session, **info)
    album.tracks.append(track)

    return artist, album, track

def store_directory(basedir, valid_types=valid_types, adaptor=adaptor):
    start = time()
    i = 0
    for file in find(basedir, valid_types):
        file = File(file, easy=True)
        
        try:
            artist, album, track = adapt_track(file)
            print(
                " * Storing: {0.name} - {1.name} - {2.name}"
                "".format(artist, album, track))
            i += 1
            models.db.session.commit()
        except KeyError:
            pass
    
    end = int(time() - start)
    print(" * Stored {} files. \n * Took {} seconds".format(i, end))
