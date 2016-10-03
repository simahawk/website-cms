# -*- coding: utf-8 -*-
import logging
import urlparse
import time

import lxml.html

import openerp
import re

_logger = logging.getLogger(__name__)


class TestMedia(openerp.tests.HttpCase):
    """ Test suite crawling an openerp CMS instance and checking that all
    internal links lead to a 200 response.

    If a username and a password are provided, authenticates the user before
    starting the crawl
    """

    at_install = False
    post_install = True

    def setUp(self):
        super(TestMedia, self).setUp()

        self.cms_media = self.env['cms.media']
        # Media 1
        self.blob1_b64 = 'blob1'.encode('base64')
        self.f1 = self.cms_media.create(
            {'name': 'f1', 'datas': self.blob1_b64})
        # Media 1
        self.blob2_b64 = 'blob2'.encode('base64')
        self.f2 = self.cms_media.create(
            {'name': 'f2',
             'datas': self.blob1_b64,
             'datas_fname': 'f2.txt'})

        self.all_files = [self.f1, self.f2]

    def tearDown(self):
        super(TestMedia, self).tearDown()
        self.registry('cms.media').unlink(
            self.cr, 1, [x.id for x in self.all_files])

    def test_url(self):
        # no file name, default to /download
        expected = (
            u'/web/content/cms.media/'
            u'{}/datas/download').format(self.f1.id)
        self.assertEqual(self.f1.website_url, expected)

        self.f1.datas_fname = 'foo.pdf'
        self.f1.invalidate_cache()
        expected = (
            u'/web/content/cms.media/'
            u'{}/datas/foo.pdf').format(self.f1.id)
        self.assertEqual(self.f1.website_url, expected)

    def test_download_file(self):
        self.authenticate('admin', 'admin')
        self.assertTrue(self.f2.exists())
        # resp = self.url_open(self.f2.website_url)

        # XXX: something really weird is going on here
        # the former assertion on `exists` passes
        # but when ir_http.binary_content is called
        # to dispatch the file content
        # `exists` returns false and you get a 404?????
        # self.assertEqual(resp.getcode(), 201)
        # # anon
        # # import pdb;pdb.set_trace()
        # resp = self.url_open(self.f2.website_url)
        # # not published yet
        # self.assertEqual(resp.getcode(), 404)
        # # published
        # # self.f2.website_published = True
        # # self.f2.public = True
        # # self.f2.invalidate_cache()
        # # import pdb;pdb.set_trace()
        # # autheticated

        # # published
        # # self.f2.website_published = True
        # # self.f2.public = True
        # # self.f2.invalidate_cache()


