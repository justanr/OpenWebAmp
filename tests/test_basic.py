import unittest

from flask import current_app

from app import configs, create_app, db

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(__name__, configs['testing'], exts=[db])
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_test(self):
        self.assertTrue(current_app.config['TESTING'])
