import unittest
from uuid import uuid4

from app import configs, create_app, schemas
from app.models import db
from app import models

from app.utils.tests import GenericCls, GenericObj


app = create_app(__name__, configs['testing'], exts=[db])
context = app.app_context()

def setUpModule():
    global db, context
    context.push()
    db.create_all()

    artist = models.Artist(name='The Foo Bars')
    album = models.Album(name="Foo Bar'd")
    artist.albums.append(album)
    tracks = [
        models.Track(
            name='Bar',
            location='bar',
            length=244,
            artist=artist,
            stream='gggg'
            ),
        models.Track(
            name='Spam',
            location='spam',
            length=244,
            artist=artist,
            stream='hhhh'
            )
        ]

    album.tracks.extend(tracks)

    member = models.Member(name='Dee', email='d@d.com', password='d')
    asp = models.Playlist(name='CharDee MacDennis')
    asp.tracks.append(tracks[0])
    member.playlists.append(asp)

    db.session.add(artist)
    db.session.add(member)
    db.session.commit()


def tearDownModule():
    global db, context
    db.drop_all()
    context.pop()

class SchemaTestCase(unittest.TestCase):
    pass       

class BaseSchemaTestCase(SchemaTestCase):

    def test_only_id_and_name(self):
        thefoobars = models.Artist.query.get(1)
        data = schemas.BaseSchema(thefoobars).data
        self.assertEqual(data, {'id':1, 'name':'The Foo Bars'})

class AlbumSchemaTestCase(SchemaTestCase):

    def test_expected_output(self):
        album = models.Album.query.get(1)
        data = schemas.TracklistSchema(album).data
        
        # this how the output *should* look
        expected = {
            'id' : 1,
            'name' : "Foo Bar'd",
            'owner' : {
                'id' : 1,
                'name' : 'The Foo Bars'
                },
            'tracks' : [
                {
                    'id': 1,
                    'name' : 'Bar'
                    },
                {
                    'id' : 2,
                    'name' : 'Spam'
                    }
                ]
            }

        self.assertEqual(data, expected)

class TrackSchemaTestCase(SchemaTestCase):
    
    def test_expected_output(self):
        track = models.Track.query.get(1)
        data = schemas.TrackSchema(track).data

        expected = {
            'id' : 1,
            'name' : 'Bar',
            'stream' : 'gggg',
            'artist' : {
                'id' : 1,
                'name' : 'The Foo Bars'
                },
            'length' : '04:04',
            'tracklists' :[
                {
                    'id' : 1,
                    'name' : "Foo Bar'd"
                    },
                {
                    'id' : 2,
                    'name' : 'CharDee MacDennis'
                    }
                ]
            }
        self.assertEquals(data, expected)

