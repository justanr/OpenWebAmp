import unittest

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
