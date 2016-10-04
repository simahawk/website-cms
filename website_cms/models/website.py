# -*- coding: utf-8 -*-

# pylint: disable=E0401

from openerp import models
from openerp import api
from openerp import tools
from openerp.addons.web.http import request
from openerp.addons.website.models.website import unslug

from openerp.addons.website_cms.utils import AttrDict

import urlparse
import urllib


class Website(models.Model):
    """Override website model."""

    _inherit = "website"

    @api.model
    @tools.ormcache('max_depth', 'pages', 'nav', 'type_ids', 'published')
    def get_nav_pages(self, max_depth=3, pages=None,
                      nav=True, type_ids=None,
                      published=True):
        """Return pages for navigation.

        Given a `max_depth` build a list containing
        a hierarchy of menu and sub menu.
        Only `cms.page` having these flags turned on:
        * `website_published`

        By default consider only `nav_include` items.
        You can alter this behavior by passing
        `nav=False` to list contents non enabled for nav
        or `nav=None` to ignore nav settings.

        * `type_ids`: filter pages by a list of types' ids

        By default consider only `website_cms.default_page_type` type.

        * `published`: filter pages by a publishing state
        """
        type_ids = type_ids or [
            self.env.ref('website_cms.default_page_type').id, ]
        result = []
        if pages is None:
            search_args = [
                ('parent_id', '=', False),
                ('type_id', 'in', type_ids)
            ]
            if published is not None:
                search_args.append(('website_published', '=', published))

            if nav is not None:
                search_args.append(('nav_include', '=', nav))

            sec_model = self.env['cms.page']
            pages = sec_model.search(
                search_args,
                order='sequence asc'
            )
        for item in pages:
            result.append(
                self._build_page_item(item,
                                      max_depth=max_depth,
                                      nav=nav,
                                      type_ids=type_ids,
                                      published=published)
            )
        return result

    @api.model
    def _build_page_item(self, item, max_depth=3,
                         nav=True, type_ids=None,
                         published=True):
        """Recursive method to build main menu items.

        Return a dict-like object containing:
        * `name`: name of the page
        * `url`: public url of the page
        * `children`: list of children pages
        * `nav`: nav_include filtering
        * `type_ids`: filter pages by a list of types' ids
        * `published`: filter pages by a publishing state
        """
        depth = max_depth or 3  # safe default to avoid infinite recursion
        sec_model = self.env['cms.page']
        # TODO: consider to define these args in the main method
        search_args = [
            ('parent_id', '=', item.id),
        ]
        if published is not None:
            search_args.append(('website_published', '=', published))
        if nav is not None:
            search_args.append(('nav_include', '=', nav))
        if type_ids is not None:
            search_args.append(('type_id', 'in', type_ids))
        subs = sec_model.search(
            search_args,
            order='sequence asc'
        )
        while depth != 0:
            depth -= 1
            children = [self._build_page_item(x, max_depth=depth)
                        for x in subs]
        res = AttrDict({
            'id': item.id,
            'name': item.name,
            'url': item.website_url,
            'children': children,
            'website_published': item.website_published,
        })
        return res

    @api.model
    def safe_image_url(self, record, field, size=None, check=True):
        """Return image url if exists."""
        sudo_record = record.sudo()
        if hasattr(sudo_record, field):
            if not getattr(sudo_record, field) and check:
                # no image here yet
                return ''
            return self.image_url(record, field, size=size)
        return ''

    @api.model
    def download_url(self, item, field_name, filename=''):
        if not filename:
            # TODO: we should calculate the filename from the field
            # but in some cases we do not have a proxy for the value
            # like for attachments, so we don't have a way
            # to get the original name of the file.
            filename = 'download'
        url = '/web/content/{model}/{ob_id}/{field_name}/{filename}'
        return url.format(
            model=item._name,
            ob_id=item.id,
            field_name=field_name,
            filename=filename,
        )

    @api.model
    def get_media_categories(self, active=True):
        """Return all available media categories."""
        return self.env['cms.media.category'].search(
            [('active', '=', active)])

    def get_alternate_languages(self, cr, uid, ids,
                                req=None, context=None,
                                main_object=None):
        """Override to drop not available translations."""
        langs = super(Website, self).get_alternate_languages(
            cr, uid, ids, req=req, context=context)

        avail_langs = None
        if main_object and main_object._name == 'cms.page':
            # avoid building URLs for not translated contents
            avail_transl = main_object.get_translations()
            avail_langs = [x.split('_')[0] for x in avail_transl.iterkeys()]

        if avail_langs is not None:
            langs = [lg for lg in langs if lg['short'] in avail_langs]
        return langs

    def safe_hasattr(self, item, attr):
        """Return true if given item has given attr.

        The following does not work in templates:

        <t t-if="main_object and
            getattr(main_object, 'sidebar_view_ids', None)">
        <t t-if="False">
          main_object.sidebar_view_ids => throws an error
          since there's no safe "hasattr" when evaluating

          QWebException: "'NoneType' object is not callable" while evaluating
          "main_object and getattr(main_object, 'sidebar_view_ids', None)"
        </t>

        evaluating `hasattr` or `getattr` in template fails :S
        """
        return hasattr(item, attr)

    def referer_to_page(self):
        """Translate HTTP REFERER to cms page if possible."""
        ref = request.httprequest.referrer
        if not ref:
            return None
        parsed = urlparse.urlparse(ref)
        if parsed.path.startswith('/cms'):
            last_bit = parsed.path.split('/')[-1]
            page_id = unslug(last_bit)[-1]
            return request.env['cms.page'].browse(page_id)
        return None

    def is_cms_page(self, obj):
        """Check if given obj is a cms page."""
        return obj is not None and getattr(obj, '_name', None) == 'cms.page'

    def cms_add_link(self, main_object=None):
        """Retrieve add cms page link."""
        # TODO: avoid adding sub pages inside news.
        # In the future we might consider controlling this
        # via cms.page.type configuration

        url = '/cms'
        if self.is_cms_page(main_object):
            news_type = request.env.ref('website_cms.news_page_type')
            if main_object.type_id.id != news_type.id:
                url = main_object.website_url
            elif main_object.parent_id \
                    and main_object.parent_id.type_id.id != news_type.id:
                url = main_object.parent_id.website_url
        return '{}/add-page'.format(url)

    def cms_edit_link(self, main_object=None):
        """Retrieve edit cms page link."""
        if self.is_cms_page(main_object):
            return '{}/edit-page'.format(main_object.website_url)
        return ''

    def cms_edit_backend_link(self, main_object=None):
        """Retrieve edit in backend cms page link."""
        base = "/web#return_label=Website"
        data = {
            'view_type': 'form',
            'model': main_object._name,
            'id': main_object.id,
        }
        if self.is_cms_page(main_object):
            data['action'] = self.env.ref('website_cms.action_cms_pages').id
        qstring = urllib.urlencode(data)
        return '{}&{}'.format(base, qstring)

    def cms_can_edit(self, main_object=None):
        """Retrieve edit cms page link."""
        if self.is_cms_page(main_object):
            is_manager = self.env.user.has_group('website_cms.cms_manager')
            is_owner = main_object.create_uid.id == self.env.user.id
            return is_owner or is_manager
        return False
