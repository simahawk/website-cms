# Copyright 2018 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import odoo.tests.common as test_common
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from mock import patch
from .fake_models import CoremetadataModel


def dt_fromstring(dt):
    return datetime.strptime(dt, DEFAULT_SERVER_DATETIME_FORMAT)


class TestContent(test_common.SavepointCase):

    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        CoremetadataModel._test_setup(cls.env)

    @classmethod
    def tearDownClass(cls):
        CoremetadataModel._test_teardown(cls.env)
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        mod = 'odoo.addons.cms_mixin.models.coremetadata.fields.Datetime'
        self.patcher = patch(mod)
        self.mock_datetime = self.patcher.start()

    @property
    def model(self):
        return self.env['fake.coremetadata']

    def _freeze_date(self, dt_string):
        dt = dt_fromstring(dt_string)
        self.mock_datetime.now.return_value = dt

    def test_published_create(self):
        now = '2018-03-02 14:30:00'
        self._freeze_date(now)

        item = self.model.create({'name': 'Foo', 'website_published': True})
        self.assertTrue(item.website_published)
        self.assertEqual(item.publish_uid.id, self.env.user.id)
        self.assertEqual(item.publish_date, now)

    def test_published_write(self):
        item = self.model.create({'name': 'Foo'})
        self.assertFalse(item.website_published)
        self.assertFalse(item.publish_uid)

        now = '2018-03-02 14:30:00'
        self._freeze_date(now)
        item.website_published = True
        self.assertEqual(item.publish_uid.id, self.env.user.id)
        self.assertEqual(item.publish_date, now)
