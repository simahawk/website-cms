# Copyright 2018 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import odoo.tests.common as test_common
from .fake_models import OrderableModel


class TestContent(test_common.SavepointCase):

    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        OrderableModel._test_setup(cls.env)

    @classmethod
    def tearDownClass(cls):
        OrderableModel._test_teardown(cls.env)
        super().tearDownClass()

    @property
    def model(self):
        return self.env['fake.orderable']

    def test_default_ordering(self):
        items = {}
        for i in range(1, 6):
            items[i] = self.model.create({'name': str(i)})

        all_items = self.model.search([])

        # 1st item should be last
        self.assertEqual(all_items[0].name, '5')

        # all items must have a sequence greater than following
        for i in range(5):
            curr = all_items[i]
            nxt = all_items[i + 1:]
            for item in nxt:
                self.assertTrue(curr.sequence > item.sequence)

    def test_ordering_tweaking(self):
        items = {}
        for i in range(1, 6):
            items[i] = self.model.create({'name': str(i)})

        items[2].sequence = 10
        items[4].sequence = 0

        all_items = self.model.search([])

        # 3rd item should be 1st
        self.assertEqual(all_items[0].name, '2')
        # 5th item should be last
        self.assertEqual(all_items[-1].name, '4')
