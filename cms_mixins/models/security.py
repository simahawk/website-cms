# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp import models, fields, api
from openerp.addons.website.models import ir_http

from werkzeug.exceptions import NotFound


class CMSSecurityMixin(models.AbstractModel):
    """Provide basic logic for protecting website items."""

    _name = "cms.security.mixin"
    _description = "A mixin for protecting website content"

    # TODO: add record rules automatically
    # When an object inherits form this mixin
    # we should create record rules for the real model.
    view_group_ids = fields.Many2many(
        string='View Groups',
        comodel_name='res.groups',
        help=("Restrict `view` access to this item to specific groups. "
              u"No group means anybody can see it.")
    )
    write_group_ids = fields.Many2many(
        string='View Groups',
        comodel_name='res.groups',
        help=("Restrict `view` access to this item to specific groups. "
              u"No group means anybody can see it.")
    )

    @api.model
    def check_permission(self, obj=None, mode='view', raise_exception=False):
        """Check permission on given object.

        @param `obj`: the item to check.
        If not `obj` is passed `self` will be used.

        @param `mode`: the permission mode to check.
        """
        obj = obj or self
        try:
            obj.check_access_rights(mode)
            obj.check_access_rule(mode)
            can = True
        except Exception:
            if raise_exception:
                raise
            can = False
        return can


class SecureModelConverter(ir_http.ModelConverter):
    """A new model converter w/ security check.

    The base model converter is responsible of converting a slug
    to a real browse object. It works fine except that
    it raises permissions errors only when you access instance fields
    in the template.

    We want to intercept this on demand and apply security check,
    so that whichever model exposes `cms.security.mixin`
    capabilities and uses this route converter,
    will be protected based on mixin behaviors.

    You can use it as usual like this:

        @http.route(['/foo/<model("my.model"):main_object>'])
    """

    def to_python(self, value):
        """Get python record and check it.

        If no permission here, just raise a NotFound!
        """
        record = super(SecureModelConverter, self).to_python(value)
        if isinstance(record, CMSSecurityMixin) \
                and not record.check_permission(mode='view'):
            raise NotFound()
        return record


class IRHTTP(models.AbstractModel):
    """Override to add our model converter.

    The new model converter make sure to apply security checks.

    See `website.models.ir_http` for default implementation.
    """

    _inherit = 'ir.http'

    def _get_converters(self):
        return dict(
            super(IRHTTP, self)._get_converters(),
            model=SecureModelConverter,
        )
