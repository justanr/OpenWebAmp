import unittest

from app.utils import tests

class GenericTestCase(unittest.TestCase):

    def setUp(self):
        self.stuff = {
            'id' : 4,
            'name' : 'Test',
            'description' : 'A test for app.utils.tests.GenericCls'
            }

    def test_GenericCls(self):
        GenericStuffCls = tests.GenericCls('Stuff', clsattrs=self.stuff)
        self.assertTrue(GenericStuffCls.__name__ == 'Stuff')
        self.assertTrue(
            all(getattr(GenericStuffCls, k) == v for k,v in self.stuff.items())
            )

    def test_GenericCls_init(self):
        GenericStuffCls = tests.GenericCls('Stuff')
        stuff = GenericStuffCls(**self.stuff)
        self.assertTrue(
            all(getattr(stuff, k) == v for k,v in self.stuff.items())
            )

    def test_GenericCls_clsattrs(self):
        GenericStuffCls = tests.GenericCls('Stuff', clsattrs={'thing':4})
        stuff = GenericStuffCls(**self.stuff)

        self.assertTrue(stuff.thing == GenericStuffCls.thing)

        GenericStuffCls.other_thing = 'a name perhaps'
        self.assertTrue(stuff.other_thing == GenericStuffCls.other_thing)


    def test_GenericCls_identity(self):
        GenericStuffCls = tests.GenericCls('Stuff', clsattrs={'x':4})
        GenericOtherCls = tests.GenericCls('Stuff', clsattrs={'x':5})

        self.assertTrue(GenericStuffCls.x != GenericOtherCls.x)

    def test_GenericObj(self):
        stuff = tests.GenericObj('Stuff', **self.stuff)
        self.assertTrue(stuff.__class__.__name__ == 'Stuff')
        self.assertTrue(
            all(getattr(stuff, k) == v for k,v in self.stuff.items())
            )

    def test_GenericObj_identity(self):
        stuff = tests.GenericObj('Stuff', **self.stuff)
        other = tests.GenericObj('Stuff', **self.stuff)

        self.assertFalse(isinstance(stuff, other.__class__))
