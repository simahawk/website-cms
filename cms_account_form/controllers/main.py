# -*- coding: utf-8 -*-
# © 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request
from odoo.addons.website_portal.controllers.main import website_account

from odoo.addons.cms_form.controllers.main import FormControllerMixin


class MyAccount(website_account, FormControllerMixin):

    @http.route(['/my/account'], type='http', auth="user", website=True)
    def details(self, **kw):
        """Replace with cms form."""
        model = 'res.partner'
        user = request.env['res.users'].browse(request.uid)
        partner = user.partner_id
        return self.make_response(model, model_id=partner.id, **kw)

    def form_model_key(self, model):
        """Return a valid form model."""
        return 'cms.form.my.account'
