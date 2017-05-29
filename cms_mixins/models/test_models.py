# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, tools
import os

testing = tools.config.get('test_enable') or os.environ.get('ODOO_TEST_ENABLE')

if testing:
    class SecuredModel(models.AbstractModel):

        _name = 'testmodel.secured'
        _inherit = [
            'cms.security.mixin',
            'website.published.mixin',
        ]
