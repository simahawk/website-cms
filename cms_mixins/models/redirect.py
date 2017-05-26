# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# TODO: and maybe integrate website_seo_redirection?
#
# from openerp import models, fields, api, _
# from ..utils import AttrDict

#
# class CMSRedirectMixin(models.AbstractModel):
#     """Handle redirection for inheriting objects.
#
#     Fields:
#     * `redirect_to_id`
#     """
#
#     _name = "cms.redirect.mixin"
#     _description = "CMS Redirect Mixin"
#
#     redirect_to_id = fields.Many2one(
#         string='Redirect to',
#         comodel_name='cms.redirect',
#         help=("If valued, you will be redirected "
#               u"to selected item permanently."),
#         domain=[('create_date', '=', False)]
#     )
#
#     @api.model
#     def has_redirect(self):
#         """Return true if we have a redirection."""
#         return bool(self.redirect_to_id)
#
#     @api.model
#     def get_redirect_data(self):
#         """Return redirection data."""
#         if not self.redirect_to_id:
#             return None
#         return AttrDict({
#             'url': self.redirect_to_id.website_url,
#             'status': int(self.redirect_to_id.status),
#         })
#
#
# class CMSLinkMixin(models.AbstractModel):
#     """A base mixin for a website model linking another model."""
#
#     _name = "cms.link.mixin"
#     _description = "CMS Link Mixin"
#
#     cms_page_id = fields.Many2one(
#         string='CMS Page',
#         comodel_name='cms.page',
#     )
#     view_id = fields.Many2one(
#         string='Odoo View',
#         comodel_name='ir.ui.view',
#         domain=[('page', '=', True)]
#     )
#     url = fields.Char(
#         'Custom URL',
#     )
#     website_url = fields.Char(
#         string='Website URL',
#         compute='_compute_website_url',
#         readonly=True
#     )
#
#     @api.multi
#     def _compute_website_url(self):
#         """Compute redirect URL."""
#         for item in self:
#             if item.url:
#                 item.website_url = item.url
#                 continue
#             if item.view_id:
#                 item.website_url = '/page/{}'.format(item.view_id.key)
#                 continue
#             if item.cms_page_id:
#                 item.website_url = item.cms_page_id.website_url
#                 continue
#
#     @api.multi
#     def name_get(self):
#         """Format displayed name."""
#         res = []
#         for item in self:
#             name = [
#                 'Go to >',
#             ]
#             if self.url:
#                 name.append(item.url[:50])
#             if self.view_id:
#                 name.append('View:' + item.view_id.name)
#             if self.cms_page_id:
#                 name.append('Page: ' + self.cms_page_id.name)
#             name.append('| Status: ' + self.status)
#             res.append((item.id, ' '.join(name)))
#         return res
#
#
# class CMSRedirect(models.Model):
#     """Handle redirection for `cms.page` model."""
#
#     _name = "cms.redirect"
#     _inherit = "cms.link.mixin"
#     _description = "CMS Redirect record"
#
#     name = fields.Char(
#         string='Description',
#     )
#     status = fields.Selection(
#         string='Redirect HTTP Status',
#         default=u'301',
#         selection='_selection_status',
#     )
#
#     @api.model
#     def _selection_status(self):
#         return [
#             ('301', _("301 Moved Permanently")),
#             ('307', _("307 Temporary Redirect")),
#         ]
