import unittest
from uuid import uuid4

from app import configs, create_app, db, models, Permissions

class ModelTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(__name__, configs['testing'], exts=[db])
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

members = [
    {
        'name' : 'catlover',
        'password' : 'cat',
        'email' : 'cat@bar.com'
    },

    {
        'name' : 'user123',
        'password' : '1234',
        'email' : '123@bar.com'
    },

    {
        'name' : 'dogzrule',
        'password' : 'catssuck',
        'email' : 'dogz314@bar.com'
    }
    ]


class MemberTestCase(ModelTestCase):

    def test_member_init(self):
        u = models.Member(**members[0])
        db.session.add(u)
        db.session.commit()
        self.assertTrue(u.id)
    
    def test_password_setter(self):
        u = models.Member(**members[1])
        self.assertTrue(u.password_hash is not None)
        self.assertFalse(u.password_hash == members[1]['password'])

    def test_no_password_getter(self):
        u = models.Member(**members[0])
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verify(self):
        u = models.Member(**members[0])
        self.assertTrue(u.verify_password(members[0]['password']))
        self.assertFalse(u.verify_password('asfasg'))

    def test_password_salts_are_different(self):
        u1 = models.Member(**members[1])
        u2 = models.Member(**members[1])

        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_member_permissions(self):
        u = models.Member(**members[1])
        db.session.add(u)
        db.session.commit()
        self.assertTrue(u.can(Permissions.STREAM))
        self.assertFalse(u.can(Permissions.MODERATE))

    def test_find_or_create(self):
        u1 = models.Member.find_or_create(session=db.session, **members[2])
        u2 = models.Member.find_or_create(session=db.session, **members[2])
        self.assertTrue(u1 is u2)


class ArtistTestCase(ModelTestCase):
    
    def test_add_album(self):
        thefoobars = models.Artist(name='The Foo Bars')
        self.assertFalse(len(thefoobars.albums))

        thefoobars.albums.append(models.Album(name="Foobar'd"))
        self.assertTrue(len(thefoobars.albums))

class AlbumTestCase(ModelTestCase):
   
    def setUp(self):
        self.thefoobars = models.Artist(name='The Foo Bars')
        self.tracks = [
            models.Track(
                name='Baz',
                stream=str(uuid4()),
                position=1,
                length=244,
                artist=self.thefoobars,
                location='/1'
                ),
            models.Track(
                name='Spam',
                stream=str(uuid4()),
                position=2,
                length=244,
                artist=self.thefoobars,
                location='/2'             
                )
            ]
        db.session.add(self.thefoobars)
        db.session.add_all(self.tracks)

    def tearDown(self):
        db.session.remove()

    def test_artist_owned(self):
        foo_bar_d = models.Album(name="Foo Bar'd", artist=self.thefoobars)
        self.assertTrue(foo_bar_d.artist == self.thefoobars)

    def test_add_tracks(self):
        foo_bar_d = models.Album(name="Foo Bar'd", artist=self.thefoobars)
        self.assertFalse(len(foo_bar_d.tracks))

        foo_bar_d.tracks.extend(self.tracks)
        self.assertTrue(len(foo_bar_d.tracks) == 2)

class TrackTestCase(ModelTestCase):
    
    def setUp(self):
        self.thefoobars = models.Artist(name='The Foo Bars')
        self.foo_bar_d = models.Album(name="Foo Bar'd", artist=self.thefoobars)
        db.session.add(self.thefoobars)

    def tearDown(self):
        db.session.remove()

    def test_artist_owned(self):
        baz = models.Track(
            name='Baz',
            length=244,
            position=1,
            artist=self.thefoobars,
            album=self.foo_bar_d,
            location='/',
            stream=str(uuid4())
            )

        db.session.add(baz)
        self.assertTrue(baz.artist is self.thefoobars)
