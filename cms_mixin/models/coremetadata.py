# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class CMSCoreMetadataMixin(models.AbstractModel):
    """Expose core fields to be usable in backend and frontend.

    Fields:
    * `create_date`
    * `create_uid`
    * `write_date`
    * `write_uid`
    * `publish_date`
    * `publish_uid`
    """

    _name = "cms.coremetadata.mixin"
    _description = "A mixin for exposing core metadata fields"

    create_date = fields.Datetime(
        'Created on',
        select=True,
        readonly=True,
    )
    create_uid = fields.Many2one(
        'res.users',
        'Author',
        select=True,
        readonly=True,
    )
    write_date = fields.Datetime(
        'Created on',
        select=True,
        readonly=True,
    )
    write_uid = fields.Many2one(
        'res.users',
        'Last Contributor',
        select=True,
        readonly=True,
    )
    publish_date = fields.Datetime(
        'Published on',
    )
    publish_uid = fields.Many2one(
        'res.users',
        'Published by',
        select=True,
        readonly=True,
    )

    @api.model
    def create(self, vals):
        """Update published date."""
        if vals.get('website_published'):
            vals['publish_date'] = fields.Datetime.now()
            vals['publish_uid'] = self.env.user.id
        return super(CMSCoreMetadataMixin, self).create(vals)

    @api.multi
    def write(self, vals):
        """Update published date."""
        if vals.get('website_published'):
            vals['publish_date'] = fields.Datetime.now()
            vals['publish_uid'] = self.env.user.id
        return super(CMSCoreMetadataMixin, self).write(vals)
