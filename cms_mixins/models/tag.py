# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp import models, fields, api


class CMSTagMixin(models.AbstractModel):
    """Base mixin for website tags."""

    _name = 'cms.tag.mixin'
    _description = 'CMS tag mixin'
    _order = 'name'

    name = fields.Char('Name', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

    @api.model
    def _tag_to_write_vals(self, tags=''):
        """Convert string values to tag ids.

        Almost barely copied from `website_forum.forum`.
        """
        vals = []
        existing_keep = []
        for tag in filter(None, tags.split(',')):
            if tag.startswith('_'):  # it's a new tag
                # check that not already created meanwhile
                # or maybe excluded by the limit on the search
                tag_ids = self.search([('name', '=', tag[1:])])
                if tag_ids:
                    existing_keep.append(int(tag_ids[0]))
                else:
                    if len(tag) and len(tag[1:].strip()):
                        vals.append((0, 0, {'name': tag[1:]}))
            else:
                existing_keep.append(int(tag))
        vals.insert(0, [6, 0, existing_keep])
        return vals
