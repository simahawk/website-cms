# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp import models, fields, api, tools
from openerp.addons.website.models.website import slug


def to_slug(item):
    """Force usage of item.name."""
    value = (item.id, item.name)
    return slug(value)


class CMSContentMixin(models.AbstractModel):
    """Base model of a CMS content."""

    _name = 'cms.content.mixin'
    _description = 'CMS page content mixin'
    _order = 'sequence, id'
    _inherit = [
        'cms.orderable.mixin',
        'website.published.mixin',
        'cms.security.mixin',
    ]

    name = fields.Char(
        'Name',
        required=True,
    )
    description = fields.Text(
        'Description',
    )
    body = fields.Html(
        'HTML Body',
        sanitize=False
    )
    nav_include = fields.Boolean(
        'Nav include',
        default=False,
        help=("Decide if this item "
              u"should be included in main navigation."),
    )

    # @api.multi
    # def write(self, vals):
    #     """Make sure to refresh website nav cache."""
    #     self.ensure_one()
    #     if 'nav_include' in vals:
    #         self.env['website'].get_nav_pages.clear_caches()
    #     return super(CMSContentMixin, self).write(vals)
    #
    # @api.model
    # def create(self, vals):
    #     """Make sure to refresh website nav cache."""
    #     res = super(CMSContentMixin, self).create(vals)
    #     if 'nav_include' in vals:
    #         self.env['website'].get_nav_pages.clear_caches()
    #     return res

    @property
    def cms_url_prefix(self):
        return u'/cms/content/{}/'.format(self._name)

    @api.multi
    def _website_url(self, field_name, arg):
        """Override method defined by `website.published.mixin`."""
        res = {}
        for item in self:
            res[item.id] = self.cms_url_prefix + slug(item)
        return res

    @api.multi
    def toggle_published(self):
        """Publish / Unpublish this page right away."""
        self.write({'website_published': not self.website_published})

    @api.model
    def get_translations(self):
        """Return translations for this page."""
        return self._get_translations(page_id=self.id)

    @tools.ormcache('page_id')
    def _get_translations(self, page_id=None):
        """Return all available translations for a page.

        We assume that a page is translated when the name is.
        """
        query = """
            SELECT lang,value FROM ir_translation
            WHERE res_id={page_id}
            AND state='translated'
            AND type='model'
            AND name='cms.page,name'
        """.format(page_id=page_id)
        self.env.cr.execute(query)
        res = self.env.cr.fetchall()
        return dict(res)
