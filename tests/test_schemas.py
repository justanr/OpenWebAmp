import unittest
from uuid import uuid4

from app import configs, create_app, schemas
from app.schemas import ma

from app.utils.tests import GenericCls, GenericObj

test_app = None

def setUpModule():
    global test_app
    test_app = create_app(__name__, configs['testing'], exts=[ma])

def tearDownModule():
    global test_app
    del test_app

class SchemaTestCase(unittest.TestCase):

    def setUp(self):
        global test_app
        self.context = test_app.app_context()
        self.context.push()

    def tearDown(self):
        self.context.pop()

class BaseSchemaTestCase(SchemaTestCase):

    def setUp(self):
        super(BaseSchemaTestCase, self).setUp()
        self.artist = GenericObj(
            'Artist', 
            name='The Foo Bars',
            id=1,
            slug='the+foo+bars'
            )

    def test_only_id_and_name(self):
        
        data = schemas.BaseSchema(self.artist).data
        self.assertEqual(data, {'slug':'the+foo+bars', 'name':'The Foo Bars'})

@unittest.skip('unused')
class AlbumSchemaTestCase(SchemaTestCase):
    
    def test_expected_output(self):
        pass

@unittest.skip('unused')
class TrackSchemaTestCase(SchemaTestCase):
    
    def test_expected_output(self):
        pass
