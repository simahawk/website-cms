# Copyright 2018 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import odoo.tests.common as test_common
from .fake_models import ContentModel


class TestContent(test_common.SavepointCase):

    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ContentModel._test_setup(cls.env)

    @classmethod
    def tearDownClass(cls):
        ContentModel._test_teardown(cls.env)
        super().tearDownClass()

    @property
    def model(self):
        return self.env['fake.content']

    def test_default_fields(self):
        item = self.model.create({
            'name': 'Foo',
            'description': 'Just testing this fake model',
            'body': '<p><strong>Yeah!</strong> HTML here!</p>',
        })
        self.assertEqual(item.name, 'Foo')
        self.assertEqual(item.description, 'Just testing this fake model')
        self.assertEqual(item.body, '<p><strong>Yeah!</strong> HTML here!</p>')

    def test_toggle_published(self):
        item = self.model.create({'name': 'Publish me pls!'})
        self.assertFalse(item.website_published)
        self.assertFalse(item.publish_uid)
        self.assertFalse(item.publish_date)
        item.toggle_published()
        self.assertTrue(item.website_published)
        self.assertTrue(item.publish_uid)
        self.assertTrue(item.publish_date)
