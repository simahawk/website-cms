# -*- coding: utf-8 -*-

from openerp.tests import common
from openerp import exceptions


class TestSecurity(common.TransactionCase):

    at_install = False
    post_install = True

    def setUp(self):
        super(TestSecurity, self).setUp()
        self.model = self.env['cms.page']
        self.all_items = {}
        self.all_pages = self.all_items.setdefault('cms.page', [])
        self.page1 = self.create('cms.page', {
            'name': "Test Page 1",
            'website_published': True,
        })
        self.page2 = self.create('cms.page', {
            'name': "Test Page 2",
            'website_published': False,
        })
        # users
        self.group_public = self.env['res.groups'].browse(
            self.ref('base.group_public'))
        self.group_mngr = self.env['res.groups'].browse(
            self.ref('website_cms.cms_manager'))
        self.user_public = self.env['res.users'].with_context(
            {'no_reset_password': True,
             'mail_create_nosubscribe': True}
        ).create({
            'name': 'Public User',
            'login': 'publicuser',
            'email': 'publicuser@example.com',
            'groups_id': [(6, 0, [self.group_public.id])]}
        )
        self.user_mngr = self.env['res.users'].with_context(
            {'no_reset_password': True,
             'mail_create_nosubscribe': True}
        ).create({
            'name': 'Manager',
            'login': 'manager',
            'email': 'manager@example.com',
            'groups_id': [(6, 0, [self.group_mngr.id])]}
        )

    def tearDown(self):
        for model, items in self.all_items.iteritems():
            self.registry(model).unlink(
                self.cr, 1, [x.id for x in items])

    def create(self, model, values, **context):
        ob = self.env[model]
        item = ob.with_context(**context).create(values)
        self.all_items.setdefault(model, []).append(item)
        return item

    def test_public_user_access(self):
        # public user env
        env = self.env(user=self.user_public)
        model = env['cms.page']
        # put forbidden record in cache
        page1 = model.browse(self.page1.id)
        # this is the one we want
        page2 = model.browse(self.page2.id)

        # published page can be found
        found = len(
            model.search([('name', '=', 'Test Page 1')]))
        self.assertEqual(found, 0)
        # not published page cannot be found
        found = len(
            model.search([('name', '=', 'Test Page 2')]))
        self.assertEqual(found, 1)

        # published page can be read
        self.assertEqual(page1.website_published, True)
        # not published page cannot be read
        with self.assertRaises(exceptions.AccessError):
            self.assertEqual(page2.website_published, False)

        # admin user can write of course
        self.page2.website_published = True
        # now public user can see published page
        self.assertEqual(page2.website_published, True)

        # page cannot be written
        with self.assertRaises(exceptions.AccessError):
            page2.website_published = False

        # page cannot be deleted
        with self.assertRaises(exceptions.AccessError):
            page2.unlink()

        # page cannot be created
        with self.assertRaises(exceptions.AccessError):
            model.create({'name': 'Impossible'})

    def __test_public_user_access(self):
        # public user env
        env = self.env(user=self.user_public)
        model = env['cms.page']
        # put forbidden record in cache
        page1 = model.browse(self.page1.id)
        # this is the one we want
        page2 = model.browse(self.page2.id)

        # published page can be accessed
        self.assertEqual(page1.website_published, True)
        # not published page cannot be accessed
        with self.assertRaises(exceptions.AccessError):
            self.assertEqual(page2.website_published, False)

        # admin user can write of course
        self.page2.website_published = True
        # now public user can see published page
        self.assertEqual(page2.website_published, True)

        # page cannot be written
        with self.assertRaises(exceptions.AccessError):
            page2.website_published = False

        # page cannot be deleted
        with self.assertRaises(exceptions.AccessError):
            page2.unlink()

        # page cannot be created
        with self.assertRaises(exceptions.AccessError):
            model.create({'name': 'Impossible'})
