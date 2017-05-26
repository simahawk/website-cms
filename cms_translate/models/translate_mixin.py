# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp import models, api, tools


class CMSTranslateMixin(models.AbstractModel):
    """Translate mixin to allow translation of objects."""

    _name = "cms.translate.mixin"
    _description = "A mixin for providing translation features"

    # TODO: add fields and logic to handle translation without ir.translation
    # The goal is to create one item per-language.
