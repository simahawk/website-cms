# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, fields, api, exceptions, _


class CMSParentMixin(models.AbstractModel):
    """Base functionalities for parent/children structure."""

    _name = "cms.parent.mixin"
    _description = "A mixin for providing parent/children features"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'

    parent_left = fields.Integer('Left Parent', select=1)
    parent_right = fields.Integer('Right Parent', select=1)

    # TODO: right now you are forced to redifine these fields
    # on your inheriting model. It would be nice
    # if the fields' comodel_name could be setup automatically
    # to point to inheriting model.
    parent_id = fields.Many2one(
        string='Parent',
        comodel_name='cms.parent.mixin',
        domain=lambda self: self._domain_parent_id(),
    )
    children_ids = fields.One2many(
        string='Children',
        inverse_name='parent_id',
        comodel_name='cms.parent.mixin'
    )

    @api.model
    def _domain_parent_id(self):
        return []

    @api.constrains('parent_id')
    def _check_parent_id(self):
        """Make sure we cannot have parent = self."""
        if self.parent_id and self.parent_id.id == self.id:
            raise exceptions.ValidationError(
                _('You cannot set the parent to itself. '
                  'Item: "%s"') % self.name
            )

    @api.multi
    def open_children(self):
        """Action to open tree view of children pages."""
        self.ensure_one()
        domain = [
            ('parent_id', '=', self.id),
        ]
        context = {
            'default_parent_id': self.id,
        }
        context.update(self._open_children_context())
        return {
            'name': 'Children',
            'type': 'ir.actions.act_window',
            'res_model': 'cms.page',
            'target': 'current',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': context,
        }

    def _open_children_context(self):
        return {}
