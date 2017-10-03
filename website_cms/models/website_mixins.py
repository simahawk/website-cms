"""Website mixins."""

# -*- coding: utf-8 -*-

# pylint: disable=E0401
# pylint: disable=W0212
# pylint: disable=R0903
# pylint: disable=R0201


from openerp import models
from openerp import fields
from openerp import api
from openerp.tools import image as image_tools


class WebsiteImageMixin(models.AbstractModel):
    """Image mixin for website models.

    Provide fields:

    * `image` (full size image)
    * `image_medium` (`image` resized)
    * `image_thumb` (`image` resized)
    """

    _name = "website.image.mixin"
    _description = "A mixin for providing image features"

    image = fields.Binary('Image', attachment=True)
    image_medium = fields.Binary(
        'Medium',
        compute="_get_image",
        store=True,
        attachment=True
    )
    image_thumb = fields.Binary(
        'Thumbnail',
        compute="_get_image",
        store=True,
        attachment=True
    )

    @api.depends('image')
    @api.multi
    def _get_image(self):
        """Calculate resized images."""
        for record in self:
            if record.image:
                record.image_medium = \
                    image_tools.image_resize_image_big(record.image)
                record.image_thumb = \
                    image_tools.image_resize_image_medium(record.image,
                                                          size=(128, 128))
            else:
                record.image_medium = False
                record.image_thumb = False


class WebsiteOrderableMixin(models.AbstractModel):
    """Orderable mixin to allow sorting of objects.

    Add a sequence field that you can use for sorting items
    in tree views. Add the field to a view like this:

        <field name="sequence" widget="handle" />

    Default sequence is calculated as last one + 1.
    """

    _name = "website.orderable.mixin"
    _description = "A mixin for providing sorting features"
    _order = 'sequence, id'

    sequence = fields.Integer(
        'Sequence',
        required=True,
        default=lambda self: self._default_sequence()
    )

    @api.model
    def _default_sequence(self):
        last = self.search([], limit=1, order='sequence desc')
        if not last:
            return 0
        return last.sequence + 1


class WebsiteCoreMetadataMixin(models.AbstractModel):
    """Expose core fields to be usable in backend and frontend.

    Fields:
    * `create_date`
    * `create_uid`
    * `write_date`
    * `write_uid`
    * `published_date`
    * `published_uid`
    """

    _name = "website.coremetadata.mixin"
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
    published_date = fields.Datetime(
        'Published on',
    )
    published_uid = fields.Many2one(
        'res.users',
        'Published by',
        select=True,
        readonly=True,
    )

    @api.multi
    def write(self, vals):
        """Update published date."""
        if vals.get('website_published'):
            vals['published_date'] = fields.Datetime.now()
            vals['published_uid'] = self.env.user.id
        return super(WebsiteCoreMetadataMixin, self).write(vals)


class WebsiteTagMixin(models.AbstractModel):
    """Base mixin for website tags."""

    _name = 'website.tag.mixin'
    _description = 'Website tag mixin'
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
