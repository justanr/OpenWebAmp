import os

from tinytag import TinyTag as _TinyTag

from .models import db, Artist, Album, Track

def walk(basedir, ignore=None):
    assert os.path.isdir(basedir), "Walk must be provided a directory."
    for f in os.listdir(basedir):
        # keep full path around for ease of use
        fp = os.path.join(basedir, f)

        if ignore and ignore(basedir, f):
            continue

        elif os.path.isdir(fp):
            # In the words of Dave Beazly
            # Punt this off to another thing
            # Yield from is the ultimate "Not my problem"
            yield from walk(fp, ignore)

        else:
            # must be a file we want
            yield fp

def ignore(basedir, f):
    valid_types = ('mp3', 'wav', 'ogg', 'oga', 'flac')

    fp = os.path.join(basedir, f)

    # ignore hidden files and directories
    if f.startswith('.'):
        return True

    # ignore files that don't match our allowed extensions
    elif os.path.isfile(fp) and not f.lower().endswith(valid_types):
        return True

    else:
        return False


def fixer(value, ignore=(AttributeError, UnicodeEncodeError), handle=None):
    '''Actual fixer function for the fix_track function.'''

    try:
        value = value.encode('latin-1').decode('utf-8').strip()
        # matching \x03 END OF TEXT is frustrating
        # just strip out any non-printable characters
        value = ''.join(c for c in value if c.isprintable())
    except ignore as e:
        # optionally handle these errors
        if handle:
            handle(e)
    finally:
        # return the value regardless of if we fixed it
        return value

def fix_track(
    track, 
    fields=('artist', 'album', 'title', 'track', 'year', 'track_total'),
    int_convert=('track', 'year', 'track_total'),
    fixer=fixer
    ):
    '''Accepts a TinyTag or similiar object and attempts to fix it.
    
    * fields: A group of fields that require attention.
    * int_convert: a subset of fields that should be integers
    * fixer: the function that fixes the fields
    '''

    for f in fields:
        value = getattr(track, f)
        if not value:
            # value is likely none
            # there's no point in processing it
            continue
        else:
            value = fixer(value)

        if f in int_convert:
            try:
                value = int(value)
            except ValueError:
                # won't convert for some reason
                # set value to 0 since we're expecting
                # an int on the other side
                value = 0

        setattr(track, f, value)
    
    # TinyTag stores duration as a float
    track.duration = int(track.duration)

    # allows us to be flexible
    return track

def TinyTag(track):
    '''wrapper function to TinyTag.get that automatically
    fixes track issues for us.'''
    return fix_track(_TinyTag.get(track), fixer=fixer)

adaptor = lambda t: {
    'artist':t.artist,
    'album':t.album,
    'name':t.title,
    'position':t.track,
    'length':t.duration
    }


def store_metadata(track, adaptor=adaptor):
    '''Accepts a TinyTag object and an optional adaptor and breaks the metadata
    into useable pieces for the SQLAlchemy models.
    '''

    info = adaptor(track)

    artist = Artist.query.filter_by(name=info['artist']).first()
    if not artist:
        artist = Artist(name=info['artist'])
        db.session.add(artist)
    info['artist'] = artist

    album = Album.query.filter_by(name=info['album'], artist=artist).first()
    if not album:
        album = Album(name=info['album'], artist=artist)
        db.session.add(album)
    info['album'] = album

    track = Track(**info)
    db.session.add(track)
    db.session.commit()
    return artist, album, track

