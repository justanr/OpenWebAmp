import unittest
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

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

    def test_add_playlist(self):
        u = models.Member(**members[0])
        apl = models.Playlist(name='Test')
        u.playlists.append(apl)

        self.assertTrue(u.playlists)
        self.assertTrue(apl.owner is u)

class ArtistTestCase(ModelTestCase):

    def setUp(self):
        self.member = models.Member.find_or_create(db.session, **members[0])
        self.tag = models.Tag.find_or_create(db.session, name='Rock')
        db.session.commit()

    def tearDown(self):
        pass

    def test_add_album(self):
        thefoobars = models.Artist(name='The Foo Bars')
        self.assertFalse(len(thefoobars.albums))

        foo_bar_d = models.Album(name="Foobar'd")
        thefoobars.albums.append(foo_bar_d)
        self.assertTrue(len(thefoobars.albums))
        self.assertTrue(foo_bar_d.owner is thefoobars)

    def test_add_tracks(self):
        thefoobars = models.Artist(name='The Foo Bars')
        baz = models.Track(
            name='Baz',
            length=244,
            artist=thefoobars,
            location='/'
            )

        self.assertTrue(thefoobars.tracks.count() == 1)

    def test_top_tags(self):
        thefoobars = models.Artist(name='The Foo Bars')
        thefoobars._tags.append(
            models.MemberTaggedArtist(
                tag=self.tag,
                member=self.member
                )
            )
        db.session.commit()
        self.assertIs(thefoobars.top_tags[0][0], self.tag)

class TracklistTestCase(ModelTestCase):
    
    def setUp(self):
        member = models.Member(name='Test', email='a@a.com', password='1')
        art = models.Artist(name='Testee')
        self.album = models.Album(name='Album Member', owner=art)
        self.playlist = models.Playlist(name='Playlist Member', owner=member)

        db.session.add_all([self.album, self.playlist])
        db.session.commit()

    def test_polymorphic_query(self):
        q = models.Tracklist.query.order_by(models.Tracklist.id).all()

        self.assertTrue(isinstance(q[0], models.Album))
        self.assertTrue(isinstance(q[1], models.Playlist))

class AlbumTestCase(ModelTestCase):
   
    def setUp(self):
        self.thefoobars = models.Artist(name='The Foo Bars')
        self.tracks = [
            models.Track(
                name='Baz',
                length=244,
                artist=self.thefoobars,
                location='/1'
                ),
            models.Track(
                name='Spam',
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
        foo_bar_d = models.Album(name="Foo Bar'd", owner=self.thefoobars)
        self.assertTrue(foo_bar_d in self.thefoobars.albums)


    def test_add_tracks(self):
        foo_bar_d = models.Album(name="Foo Bar'd", owner=self.thefoobars)
        self.assertFalse(len(foo_bar_d.tracks))

        foo_bar_d.tracks.extend(self.tracks)
        self.assertTrue(len(foo_bar_d.tracks) == 2)

    def test_track_ordering(self):
        foo_bar_d = models.Album(name="Foo Bar'd", owner=self.thefoobars)
        foo_bar_d.tracks.extend(self.tracks)

        self.assertTrue(foo_bar_d._trackpositions[0].track is self.tracks[0])
        self.assertTrue(self.tracks[0]._trackpositions[0].position == 0)

        extra = models.Track(
            name='Another',
            length=1,
            artist=self.thefoobars,
            location='/3'
            )

        foo_bar_d.tracks.insert(0, extra)
        self.assertTrue(foo_bar_d.tracks[0] is extra)
        self.assertTrue(self.tracks[0]._trackpositions[0].position == 1)

class PlaylistTestCase(ModelTestCase):

    def setUp(self):
        self.member = models.Member(name='Dee', email='a@a.com', password='a')
        self.thefoobars = models.Artist(name='The Foo Bars')
        self.tracks = [
            models.Track(
                name='Baz',
                length=244,
                artist=self.thefoobars,
                location='/1'
                ),
            models.Track(
                name='Spam',
                length=244,
                artist=self.thefoobars,
                location='/2'             
                )
            ]
        db.session.add_all([self.thefoobars, self.member])
        db.session.add_all(self.tracks)

    def tearDown(self):
        db.session.remove()

    def test_member_owned(self):
        apl = models.Playlist(name='Chardee MacDennis', owner=self.member)

        self.assertTrue(apl in self.member.playlists)


class TrackTestCase(ModelTestCase):
    
    def setUp(self):
        self.thefoobars = models.Artist(name='The Foo Bars')
        self.foo_bar_d = models.Album(name="Foo Bar'd", owner=self.thefoobars)
        self.mem = models.Member(name='mem', email='a@a.com', password='1')
        self.apl = models.Playlist(name='apl', owner=self.mem)
        db.session.add(self.thefoobars)

    def tearDown(self):
        db.session.remove()

    def test_autogenerate_stream_id(self):
        baz = models.Track(
            name='Baz',
            length=244,
            artist=self.thefoobars,
            location='/'
            )

        db.session.commit()
        self.assertTrue(baz.stream)

    def test_artist_owned(self):
        baz = models.Track(
            name='Baz',
            length=244,
            artist=self.thefoobars,
            location='/',
            )

        self.assertTrue(baz.artist is self.thefoobars)

    def test_multiple_membership(self):
        baz = models.Track(
            name='Baz',
            length=244,
            artist=self.thefoobars,
            location='/'
            )

        self.apl.tracks.append(baz)
        self.foo_bar_d.tracks.append(baz)
    
        self.apl.tracks.append(baz)
        self.foo_bar_d.tracks.append(baz)
        self.assertTrue(
            all(tl in baz.tracklists for tl in [self.foo_bar_d, self.apl])
            )

class TagTestCase(ModelTestCase):
    
    def test_unique(self):    
        rock = models.Tag.find_or_create(db.session, name='Rock')
        other = models.Tag.find_or_create(db.session, name='Rock')
        self.assertIs(rock, other)

class MemberTaggedArtistTestCase(ModelTestCase):
    
    def test_unique_constraint(self):
        artist = models.Artist(name='The Foo Bars')
        member = models.Member(**members[0])
        tag = models.Tag(name='Rock')

        mta_1 = models.MemberTaggedArtist(
            artist=artist,
            tag=tag,
            member=member
            )

        mta_2 = models.MemberTaggedArtist(
            artist=artist,
            tag=tag,
            member=member
            )
        
        db.session.add_all([mta_1, mta_2])

        with self.assertRaises(IntegrityError) as e:
            db.session.commit()

        db.session.rollback()
        self.assertIsInstance(e.exception, IntegrityError)
