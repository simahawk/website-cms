# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, fields, api, tools


VIEW_DOMAIN = [
    ('type', '=', 'qweb'),
    ('cms_view', '=', True),
]


class CMSPage(models.Model):
    """Model of a CMS page."""

    _name = 'cms.page'
    _description = 'CMS page'
    _order = 'sequence, id'
    _inherit = [
        'cms.content.mixin',
        'cms.parent.mixin',
    ]
    type_id = fields.Many2one(
        string='Page type',
        comodel_name='cms.page.type',
        default=lambda self: self._default_type_id()
    )
    view_id = fields.Many2one(
        string='View',
        comodel_name='ir.ui.view',
        domain=lambda self: VIEW_DOMAIN,
        default=lambda self: self._default_view_id()
    )
    sub_page_type_id = fields.Many2one(
        string='Default page type for sub pages',
        comodel_name='cms.page.type',
        help=("You can select a page type to be used "
              u"by default for each contained page."),
    )
    sub_page_view_id = fields.Many2one(
        string='Default page view for sub pages',
        comodel_name='ir.ui.view',
        help=("You can select a view to be used "
              u"by default for each contained page."),
        domain=lambda self: VIEW_DOMAIN,
    )
    default_view_item_id = fields.Many2one(
        string='Default view item',
        comodel_name='cms.page',
        help=("Select an item to be used as default view "
              u"for current page."),
    )

    @api.model
    def _default_type_id(self):
        return self.env['cms.page.type'].search(
            [('default', '=', True)], limit=1)

    @api.model
    def _default_view_id(self):
        page_view = self.env.ref('website_cms.page_default')
        return page_view and page_view.id or False

    def _open_children_context(self):
        ctx = {}
        for k in ('type_id', 'view_id'):
            fname = 'sub_page_' + k
            value = getattr(self, fname)
            if value:
                ctx['default_' + k] = value.id
        return ctx

    @api.model
    def get_translations(self):
        """Return translations for this item."""
        return self._get_translations(res_id=self.id)

    @tools.ormcache('res_id')
    def _get_translations(self, res_id=None):
        """Return all available translations for a page.

        We assume that a content is translated when the name is.
        """
        query = """
            SELECT lang,value FROM ir_translation
            WHERE res_id={page_id}
            AND state='translated'
            AND type='model'
            AND name='{model},name'
        """.format(res_id=res_id, model=self._name)
        self.env.cr.execute(query)
        res = self.env.cr.fetchall()
        return dict(res)