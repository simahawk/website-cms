# Copyright 2018 Simone Orsi (Camptocamp)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, api


class CMSStatechartMixin(models.AbstractModel):
    
    _name = 'cms.statechart.mixin'
    _inherit = 'statechart.mixin'

    @api.multi
    def cms_make_state(self, state):
        handler_name = 'cms_make_state_%s' % state
        handler = getattr(self, handler_name, None)
        if handler:
            handler()

    @api.multi
    def cms_make_state_published(self):
        for item in self:
            # TODO: well, do something better
            item.website_published = True

    @api.multi
    def cms_make_state_draft(self):
        for item in self:
            # TODO: well, do something better
            item.website_published = False

    @api.multi
    def sc_actions(self):
        """List available actions."""
        self.ensure_one()
        actions = []
        disp_state_model = self.env['statechart.display_state']
        sc = self.sc_interpreter._statechart
        for state in self.sc_interpreter.configuration:
            # TODO: no better way?
            transitions = sc.transitions_from(state)
            for tr in transitions:
                target_display =  disp_state_model.search([
                    ('key', '=', '{}:{}'.format(sc.name, tr.target))
                ])
                actions.append({
                    'action': tr.event,
                    'source': tr.source,
                    'target': tr.target,
                    'target_display': target_display,
                })
        return actions


class Proposal(models.AbstractModel):
    
    _name = 'project.proposal'
    _inherit = [
        'project.proposal',
        'cms.statechart.mixin',
    ]