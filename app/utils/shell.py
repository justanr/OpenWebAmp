from __future__ import print_function

import os
import re
import sys
from uuid import uuid4
from time import time

from mutagenx import File

from sqlalchemy.exc import IntegrityError

from .. import models

valid_types=('m4a', 'flac', 'mp3', 'ogg', 'oga')

def break_tag(tag, breakers=('\\\\', '/', '&', ',', ' ',  '\\\.')):
    '''Breaks a composite tag into smaller pieces based on certain
    punctuation. Smaller tags are stripped for excess white space before
    being placed into a set.

    .. code-block:: python

        break_tag('viking / folk')  # -> {'viking', 'folk'}
        break_tag('dance & pop') # -> {'dance', 'pop'}
        break_tag('thrash metal') # -> {'thash', 'metal'}
        break_tag('progressive metal / black metal')
            # -> {'progressive', 'black', 'metal'}

    :param tag str: The tag to be analyzed and broken.
    :param breakers iterable: A group of characters to break larger tags with.
    :returns set:

    '''
    return set(t.strip() for t in re.split('|'.join(breakers), tag))

def find(basedir, valid_types=valid_types):
    '''Utilize os.walk to only select out the files we'd like to potentially
    parse and yield them one at a time.

    :param basedir str: Path to a directory to walk.
    :param valid_types iterable: An iterable of file extensions to look for.
    :yields lists:

    '''
    basedir = os.path.abspath(basedir)
    for current, dirs, files in os.walk(basedir):
        files = sorted(files)
        files = filter(lambda f: f.endswith(valid_types), files)
        files = [os.path.join(current, f) for f in files]

        if files:
            yield files

def adaptor(track):
    '''Simple object to dictionary translator. Extracts specific information
    from a mutagan file object and places it into a flat dictionary.
    '''
    return dict(
        artist=track['artist'][0],
        album=track['album'][0],
        length=int(track.info.length),
        location=track.filename,
        name=track['title'][0],
        )

def adapt_track(track, adaptor=adaptor):
    '''Translates a track file object into separate Artist, Album and Track
    OWA models.

    :param track: An object representing an audio file's metadata.
    :param adaptor callable: A callable that will translate the metadata object
        into a dictionary
    :returns tuple(Artist, Album, Track):
    '''

    info = adaptor(track)

    # ugly code to strip featuring artists from an artist's name
    # TODO: work out how to credit contributing artists somehow
    # that still preserves grouping the main artist's work together
    if 'feat.' in  info['artist']:
        info['artist'] = info['artist'].split('feat.')[0].strip()

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

    if track not in album.tracks:
        album.tracks.append(track)

    return artist, album, track

def tag_artist(genres, member, artist):
    ''' Applies tags to an artist model instance from a member model instance.

    :param genres str: A string of genres
    :param member models.Member: An instance of Member
    :param artist models.Artist: An instance of Artist
    '''
    for tag in break_tag(genres):
        if not tag:
            continue

        tag = models.Tag.find_or_create(
            models.db.session,
            name=tag
            )

        member._tags.append(
            models.MemberTaggedArtist(
                tag=tag,
                artist=artist
                )
            )

def store_directory(
    basedir,
    member=None,
    valid_types=valid_types,
    adaptor=adaptor
    ):
    '''Walks a directory and stores each track in the database.

    Reports to sys.stdout all successes and keeps a running total of time
    and files processed. Errors are reported to sys.stderr.

    Information is persisted to database in groups,
    determined by `utils.find` (which groups by directory)

    An optional member can be passed through who will tag each artist once
    with the genre information present on the first track it encounters that
    has that information.

    :param basedir str: A path to the directory to be walked
    :param member models.Member: Optional. A member to tag the artists in the
        walked directory.
    :param valid_types iterable: A collection of valid file extensions to
        examine, defaults to `('.mp3', '.ogg', '.flac', '.oga', '.m4a')`
    :param adaptor callable: A callable that will translate the audio metadata
        object into a dictionary.
    :returns None:
    '''
    start = time()
    track_count = 0
    for group in find(basedir, valid_types):
        check = True
        for file in group:
            file = File(file, easy=True)
            try:
                artist, album, track = adapt_track(file)

                if member and check and artist.id is None:
                    genre = file.get('genre', [])
                    if genre:
                        genre = genre[0]
                        tag_artist(genre, member, artist)
                    check = False

            except KeyError as e:
                print(
                    'Error processing: {}'.format(file.filename),
                    '\t{0!r}: {0!s}'.format(e),
                    file=sys.stderr,
                    sep='\n'
                    )
            else:
                print(
                    "* Processed: {0.name} - {1.name} - {2.name}"
                    "".format(artist, album, track)
                    )
        

        try:
            models.db.session.commit()
            track_count += len(group)
        except IntegrityError as e:
            models.db.session.rollback()
            print(
                'Error encountered: {}'.format(e),
                '\tArtist: {}'.format(artist.name),
                '\tAlbum: {}'.format(album.name),
                '\tTrack: {}'.format(track.name),
                file=sys.stderr,
                sep='\n'
                )
        else:
            print(
                '\t* Storing: {0.name} - {1.name}'.format(artist, album),
                file=sys.stdout
                )
            end = int(time() - start)
            print(
                "\t* Stored {} files.".format(track_count),
                "\t* Took {} seconds".format(end),
                file=sys.stdout,
                sep='\n'
                )
