import unittest

from flask import current_app

from app import configs, create_app, db

class BasicsTestCase(unittest.TestCase):

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

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_test(self):
        self.assertTrue(current_app.config['TESTING'])
