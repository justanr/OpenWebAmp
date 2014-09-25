import os
from uuid import uuid4
from time import time

from mutagenx import File

from sqlalchemy.exc import IntegrityError

from .. import models

valid_types=('m4a', 'flac', 'mp3', 'ogg', 'oga')


def find(basedir, valid_types=valid_types):
    '''Utilize os.walk to only select out the files we'd like to potentially
    parse and yield them one at a time.'''
    basedir = os.path.abspath(basedir)
    for current, dirs, files in os.walk(basedir):
        files = sorted(files)
        files = filter(lambda f: f.endswith(valid_types), files)
        files = [os.path.join(current, f) for f in files]

        if files:
            yield files


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
    for group in find(basedir, valid_types):
        for file in group:
            file = File(file, easy=True)
            try:
                artist, album, track = adapt_track(file)
            except KeyError:
                print('Error processing: {}'.format(file))
            else:
                print(
                    " * Processed: {0.name} - {1.name} - {2.name}"
                    "".format(artist, album, track)
                    )
                i += 1
        
        try:
            models.db.session.commit()
        except IntegrityError as e:
            models.db.session.rollback()
            print('Error encountered: {}'.format(e.msg)) 
        else:
            print(' * Storing: {0.name} - {1.name}'.format(artist, album))
    end = int(time() - start)
    print(" * Stored {} files. \n * Took {} seconds".format(i, end))
