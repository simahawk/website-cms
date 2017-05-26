# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp import models
from openerp import fields
from openerp import api
from openerp.tools import image as image_tools


# TODO: what if we use multi image based on
# https://github.com/OCA/server-tools/tree/9.0/base_multi_image


class CMSImageMixin(models.AbstractModel):
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
