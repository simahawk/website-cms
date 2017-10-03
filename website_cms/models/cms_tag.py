# -*- coding: utf-8 -*-

# pylint: disable=E0401
# pylint: disable=W0212
from openerp import models
from openerp import fields


class CMSTag(models.Model):
    """Model of a CMS tag."""

    _name = 'cms.tag'
    _description = 'Website tag mixin'
    _inherit = ['website.tag.mixin', ]
    _order = 'name'

    page_ids = fields.Many2many(
        string='Related pages',
        comodel_name='cms.page',
        relation='cms_tag_related_page_rel',
        column1='tag_id',
        column2='page_id',
    )
